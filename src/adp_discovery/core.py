"""Validation and composition for the repository's discovery catalog."""

import json
from functools import cache
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[2]


class DiscoveryError(ValueError):
    """An invalid discovery input with a user-facing explanation."""


def unique_mapping(items):
    result = {}
    for key, value in items:
        if not isinstance(key, str):
            raise DiscoveryError(f"mapping keys must be strings, got {key!r}")
        if key in result:
            raise DiscoveryError(f"duplicate key {key!r}")
        result[key] = value
    return result


class CatalogLoader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        return unique_mapping(self.construct_pairs(node, deep=deep))


def read_json(stream):
    return json.load(stream, object_pairs_hook=unique_mapping)


@cache
def schema_document(name):
    path = ROOT / "schemas" / f"{name}.schema.json"
    return json.loads(path.read_text(encoding="utf-8"))


@cache
def schema(name):
    document = schema_document(name)
    Draft202012Validator.check_schema(document)
    registry = Registry().with_resources(
        (f"https://adp-discovery.local/schemas/{name}.schema.json",
         Resource.from_contents(schema_document(name)))
        for name in ("state-v2", "state-v3", "template")
    )
    return Draft202012Validator(document, registry=registry)


def validate_schema(name, data, label):
    error = next(schema(name).iter_errors(data), None)
    if error:
        raise DiscoveryError(f"{label} {error.json_path}: {error.message}")


def index_by_id(items, label):
    result = {}
    for item in items:
        key = item["id"]
        if key in result:
            raise DiscoveryError(f"{label}: duplicate ID {key!r}")
        result[key] = item
    return result


def read_template(path, expected, forbidden):
    try:
        data = yaml.load(path.read_text(encoding="utf-8"), Loader=CatalogLoader)
    except (yaml.YAMLError, DiscoveryError) as error:
        raise DiscoveryError(f"{path}: {error}") from error
    except RecursionError as error:
        raise DiscoveryError(f"{path}: YAML nesting is too deep") from error
    try:
        validate_schema("template", data, path)
    except RecursionError as error:
        raise DiscoveryError(f"{path}: template nesting is too deep or contains a recursive YAML alias") from error
    if data["id"] != expected:
        raise DiscoveryError(f"{path}: id must be {expected!r}")
    if forbidden in data:
        raise DiscoveryError(f"{path}: {forbidden!r} is not allowed here")
    return data


def combine_rule_results(results, decisive):
    """Combine child results using false for an all rule or true for an any rule."""
    unresolved = set()
    for value, missing in results:
        if value is decisive:
            return decisive, set()
        unresolved.update(missing)
    if unresolved:
        return None, unresolved
    return not decisive, set()


def evaluate_rule(rule, products, tag_values):
    """Return the truth value and unresolved tags that still affect it."""
    operator, operand = next(iter(rule.items()))
    match operator:
        case "product":
            return operand in products, set()
        case "tag":
            if operand not in tag_values:
                return None, {operand}
            return tag_values[operand], set()
        case "not":
            value, unresolved = evaluate_rule(operand, products, tag_values)
            return (None if value is None else not value), unresolved
        case "all" | "any":
            return combine_rule_results(
                (evaluate_rule(child, products, tag_values) for child in operand),
                decisive=operator == "any",
            )
    raise DiscoveryError(f"unknown rule operator {operator!r}")


def check_rule_refs(rule, products, tags, label):
    operator, operand = next(iter(rule.items()))
    match operator:
        case "product" | "tag":
            choices = products if operator == "product" else tags
            if operand not in choices:
                raise DiscoveryError(f"{label}: unknown {operator} {operand!r}")
        case "not":
            check_rule_refs(operand, products, tags, f"{label}.not")
        case "all" | "any":
            for index, child in enumerate(operand):
                check_rule_refs(child, products, tags, f"{label}.{operator}[{index}]")


def applicable_entry(entry, template_result, products, tag_values):
    if "applies" not in entry:
        return template_result
    return combine_rule_results(
        (template_result, evaluate_rule(entry["applies"], products, tag_values)),
        decisive=False,
    )


class Catalog:
    def __init__(self, directory):
        base_path = directory / "base.yaml"
        self.base = read_template(base_path, "general", "applies")
        self.products = {"general": self.base}
        self.overlays = {}
        self.tags = self.base.get("tags", {})
        paths = {"general": base_path}
        for folder, destination in (("products", self.products), ("overlays", self.overlays)):
            for path in sorted((directory / folder).glob("*.yaml")):
                if path.stem in paths:
                    raise DiscoveryError(
                        f"{path}: duplicate template ID {path.stem!r}; first declared in {paths[path.stem]}"
                    )
                item = read_template(path, path.stem, "applies" if folder == "products" else "tags")
                if folder == "products" and "tags" in item:
                    raise DiscoveryError(f"{path}: declare tags in base.yaml")
                if folder == "overlays" and "applies" not in item:
                    raise DiscoveryError(f"{path}: missing applies rule")
                destination[path.stem] = item
                paths[path.stem] = path

        owners = {}
        criteria = {}
        for item in (*self.products.values(), *self.overlays.values()):
            path = paths[item["id"]]
            if "applies" in item:
                check_rule_refs(item["applies"], self.products, self.tags, f"{path} $.applies")
            for index, dimension in enumerate(item["dimensions"]):
                location = f"{path} $.dimensions[{index}]"
                key = dimension["id"]
                if key in owners:
                    previous, previous_location = owners[key]
                    fields = [
                        field for field in ("question", "required", "applies")
                        if previous.get(field) != dimension.get(field)
                    ]
                    detail = f"; conflicting fields: {', '.join(fields)}" if fields else "; identical declaration"
                    raise DiscoveryError(
                        f"duplicate dimension ID {key!r} in {previous_location} and {location}{detail}"
                    )
                owners[key] = dimension, location
                if "applies" in dimension:
                    check_rule_refs(dimension["applies"], self.products, self.tags, f"{location}.applies")
            local_dimensions = {dimension["id"] for template in (self.base, item)
                                for dimension in template["dimensions"]}
            for index, criterion in enumerate(item.get("readiness_criteria", [])):
                location = f"{path} $.readiness_criteria[{index}]"
                key = criterion["id"]
                if key in criteria:
                    raise DiscoveryError(f"duplicate readiness criterion ID {key!r} in {criteria[key]} and {location}")
                criteria[key] = location
                if "applies" in criterion:
                    check_rule_refs(criterion["applies"], self.products, self.tags, f"{location}.applies")
                if criterion["kind"] == "dimension" and criterion["dimension"] not in local_dimensions:
                    raise DiscoveryError(f"{location}: criterion dimension must come from its template or the base")
                if key == "baseline-review" and (
                    item is not self.base or criterion["kind"] != "review" or "applies" in criterion
                ):
                    raise DiscoveryError(f"{location}: baseline-review must be an unconditional base review")

    def compose(self, product, tags, *, secondary_products=(), partial=False, absent_tags=(),
                snapshot=False, readiness=False):
        """Compose a confirmed checklist or inspect applicability with partial tag facts."""
        snapshot = snapshot or readiness
        partial = partial or snapshot
        selected = (product, *secondary_products)
        products = set()
        for selection in selected:
            if selection not in self.products:
                raise DiscoveryError(f"unknown product {selection!r}")
            if selection in products:
                raise DiscoveryError(f"duplicate product selection {selection!r}")
            products.add(selection)
        if "general" in selected[1:]:
            raise DiscoveryError("'general' is the base profile and cannot be selected as a secondary product")

        present = set(tags)
        absent = set(absent_tags)
        if absent and not partial:
            raise DiscoveryError("explicit absent tags require partial inspection (--partial)")
        unknown = sorted((present | absent) - self.tags.keys())
        if unknown:
            raise DiscoveryError(f"unknown tags: {', '.join(unknown)}")
        contradictions = sorted(present & absent)
        if contradictions:
            raise DiscoveryError(f"tags declared both present and absent: {', '.join(contradictions)}")
        tag_values = dict.fromkeys(absent if partial else self.tags, False)
        tag_values.update(dict.fromkeys(present, True))

        profile = {
            "product": product,
            "tags": sorted(present),
            "overlays": [],
            "dimensions": [],
        }
        if len(selected) > 1 or partial:
            profile["secondary_products"] = list(selected[1:])
        if partial:
            profile.update(absent_tags=sorted(absent), unresolved_overlays=[], unresolved_dimensions=[])

        templates = [self.base]
        templates.extend(self.products[key] for key in selected if key != "general")
        templates.extend(self.overlays.values())
        if snapshot:
            profile.update(
                secondary_products=list(selected[1:]), absent_tags=sorted(absent),
                unresolved_overlays=[], unresolved_dimensions=[],
                inapplicable_overlays=[], inapplicable_dimensions=[],
                template_versions={item["id"]: item["version"] for item in templates},
            )
        if readiness:
            profile["readiness_criteria"] = []
        for item in templates:
            source = item["id"]
            template_result = (True, set())
            if "applies" in item:
                template_result = evaluate_rule(item["applies"], products, tag_values)
                value, missing = template_result
                if value is False and not snapshot:
                    continue
                if value is True:
                    profile["overlays"].append(source)
                elif value is None:
                    profile["unresolved_overlays"].append({"id": source, "unresolved_tags": sorted(missing)})
                else:
                    profile["inapplicable_overlays"].append(source)
            for dimension in item["dimensions"]:
                value, missing = applicable_entry(dimension, template_result, products, tag_values)
                entry = {key: dimension[key] for key in ("id", "question", "required")}
                entry["source"] = source
                if value is True:
                    profile["dimensions"].append(entry)
                elif value is None:
                    profile["unresolved_dimensions"].append({**entry, "unresolved_tags": sorted(missing)})
                elif snapshot:
                    profile["inapplicable_dimensions"].append(entry)
            if readiness:
                for criterion in item.get("readiness_criteria", []):
                    value, missing = applicable_entry(criterion, template_result, products, tag_values)
                    profile["readiness_criteria"].append({
                        "criterion": criterion, "source": source, "unresolved_tags": sorted(missing),
                        "applicability": {True: "applicable", None: "unresolved", False: "inapplicable"}[value],
                    })
        return profile

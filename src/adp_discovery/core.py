"""Validation and composition for the repository's discovery catalog."""

import json
from functools import cache
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator


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
def schema(name):
    path = ROOT / "schemas" / f"{name}.schema.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(document)
    return Draft202012Validator(document)


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

    validate_schema("template", data, path)
    if data["id"] != expected:
        raise DiscoveryError(f"{path}: id must be {expected!r}")
    if forbidden in data:
        raise DiscoveryError(f"{path}: {forbidden!r} is not allowed here")
    return data


def rule_matches(rule, product, tags):
    operator, operand = next(iter(rule.items()))
    match operator:
        case "product":
            return operand == product
        case "tag":
            return operand in tags
        case "not":
            return not rule_matches(operand, product, tags)
        case "all":
            return all(rule_matches(child, product, tags) for child in operand)
        case "any":
            return any(rule_matches(child, product, tags) for child in operand)
    raise DiscoveryError(f"unknown rule operator {operator!r}")


def check_rule_refs(rule, products, tags, label):
    operator, operand = next(iter(rule.items()))
    match operator:
        case "product" | "tag":
            choices = products if operator == "product" else tags
            if operand not in choices:
                raise DiscoveryError(f"{label}: unknown {operator} {operand!r}")
        case "not":
            check_rule_refs(operand, products, tags, label)
        case "all" | "any":
            for child in operand:
                check_rule_refs(child, products, tags, label)


class Catalog:
    def __init__(self, directory):
        self.base = read_template(directory / "base.yaml", "general", "applies")
        self.products = {"general": self.base}
        self.overlays = {}
        self.tags = self.base.get("tags", {})
        ids = {"general"}
        for folder, destination in (("products", self.products), ("overlays", self.overlays)):
            for path in sorted((directory / folder).glob("*.yaml")):
                if path.stem in ids:
                    raise DiscoveryError(f"{path}: duplicate template ID {path.stem!r}")
                item = read_template(path, path.stem, "applies" if folder == "products" else "tags")
                if folder == "products" and "tags" in item:
                    raise DiscoveryError(f"{path}: declare tags in base.yaml")
                if folder == "overlays":
                    if "applies" not in item:
                        raise DiscoveryError(f"{path}: missing applies rule")
                    check_rule_refs(item["applies"], self.products, self.tags, path)
                destination[path.stem] = item
                ids.add(path.stem)

        owners = {}
        for item in (*self.products.values(), *self.overlays.values()):
            for dimension in item["dimensions"]:
                key = dimension["id"]
                if key in owners:
                    raise DiscoveryError(f"duplicate dimension ID {key!r} in {owners[key]!r} and {item['id']!r}")
                owners[key] = item["id"]

    def compose(self, product, tags):
        if product not in self.products:
            raise DiscoveryError(f"unknown product {product!r}")
        unknown = sorted(set(tags) - self.tags.keys())
        if unknown:
            raise DiscoveryError(f"unknown tags: {', '.join(unknown)}")

        tag_set = set(tags)
        overlays = [
            item for item in self.overlays.values() if rule_matches(item["applies"], product, tag_set)
        ]
        templates = [self.base]
        if product != "general":
            templates.append(self.products[product])
        templates.extend(overlays)
        dimensions = [
            {**dimension, "source": item["id"]}
            for item in templates
            for dimension in item["dimensions"]
        ]
        return {
            "product": product,
            "tags": sorted(tag_set),
            "overlays": [item["id"] for item in overlays],
            "dimensions": dimensions,
        }

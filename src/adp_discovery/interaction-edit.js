// Each open walkthrough starts with the example values in the Markdown.
const values = new Map();
const bound = document.querySelectorAll("[data-bind]");
for (const field of document.querySelectorAll("input[data-bind]")) {
  values.set(field.dataset.bind, field.defaultValue);
}

function refresh() {
  for (const node of bound) {
    const key = node.dataset.bind;
    if (!values.has(key)) continue;
    const value = values.get(key);
    if (node instanceof HTMLInputElement) {
      node.value = value;
    } else {
      node.textContent = value;
      const link = node.closest(".action-row")?.querySelector("a");
      if (link) link.setAttribute("aria-label", link.textContent + " — " + value);
    }
  }
}

document.addEventListener("click", event => {
  const link = event.target.closest("a");
  if (!link || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
  if (link.dataset.commit) {
    for (const field of link.closest("section").querySelectorAll("input[data-bind]")) {
      values.set(field.dataset.bind, field.value);
    }
  }
  refresh();
});
window.addEventListener("hashchange", refresh);
refresh();

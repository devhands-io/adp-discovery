const guide = document.querySelector("#guide");
const heading = guide.querySelector("strong");
const instruction = guide.querySelector("p");
const feedback = guide.querySelector("small");
const scenarios = new Map(Array.from(document.querySelectorAll("[data-scenario]"),
  link => [link.dataset.scenario, link]));
const defaultPage = document.querySelector("main").dataset.default;

const nextButton = document.getElementById("next-scenario");
const prefix = "adp-progress-v1:" + document.querySelector("main").dataset.model + ":";
const memory = new Map();
let nextScenario;

function record(link) {
  const key = prefix + link.dataset.scenario;
  try {
    return JSON.parse(localStorage.getItem(key + ":" + link.dataset.signature)) || memory.get(key + ":" + link.dataset.signature) ||
      (localStorage.getItem(key) || memory.has(key) ? {signature: null} : null);
  } catch {
    return memory.get(key + ":" + link.dataset.signature) || (memory.has(key) ? {signature: null} : null);
  }
}

function progress(link) {
  const saved = record(link);
  if (!saved) return "new";
  if (saved.signature !== link.dataset.signature) return "retry";
  return saved.completed ? "done" : "started";
}

function remember(run, completed) {
  const link = scenarios.get(run.scenario);
  const previous = record(link);
  if (previous?.signature === run.signature && previous.completed && !completed) return;
  const key = prefix + run.scenario;
  const saved = {signature: run.signature, completed, run};
  memory.set(key + ":" + run.signature, saved);
  memory.set(key, true);
  try {
    localStorage.setItem(key + ":" + run.signature, JSON.stringify(saved));
    localStorage.setItem(key, "1");
  } catch {
    // Progress remains available for the current visit.
  }
}

function updateList() {
  let completed = 0;
  for (const link of scenarios.values()) {
    const state = progress(link);
    const row = link.closest(".scenario");
    row.querySelector(".status").textContent =
      {new: "", started: "In progress", done: "✓ Completed", retry: "Retry needed"}[state];
    link.textContent = {new: "Start", started: "Resume", done: "Replay", retry: "Retry"}[state];
    link.setAttribute("aria-label", link.textContent + ": " + row.querySelector("h3").textContent);
    if (state === "done") completed++;
  }
  document.getElementById("progress").textContent =
    completed + " of " + scenarios.size + " scenarios completed";
}

function reveal(id) {
  for (const node of document.querySelectorAll("[data-after]")) {
    if (node.dataset.after === id) node.hidden = false;
  }
}

nextButton.addEventListener("click", () => nextScenario?.click());
window.addEventListener("storage", event => {
  if (event.key?.startsWith(prefix)) {
    memory.delete(event.key);
    describe();
  }
});

function page() {
  return document.querySelector("section:target") || document.getElementById(defaultPage);
}

function describe() {
  updateList();
  nextButton.hidden = true;
  const screen = page();
  const run = history.state?.walkthrough;
  const scenario = scenarios.get(run?.scenario);
  guide.hidden = screen.id === "coverage";
  const guided = scenario && run.signature === scenario.dataset.signature && run.screen === screen.id;
  displayScreenNote(!guide.hidden && guided ? run : null, screen);
  if (guide.hidden) {
    for (const panel of notePanels.values()) {
      if (panel.open) displayScenarioNotes(panel);
    }
    return;
  }
  feedback.hidden = false;
  heading.textContent = scenario?.closest(".scenario").querySelector("h3").textContent || "Try the screen";
  if (!scenario || run.signature !== scenario.dataset.signature || run.screen !== screen.id) {
    instruction.textContent = "Try the action you wanted to check.";
    return;
  }
  for (const id of run.revealed || []) reveal(id);
  const steps = scenario.dataset.steps.split(" ");
  if (run.diverged) {
    instruction.textContent = "You took a different route. Use Notes to describe the path you expected, or return to the scenarios to resume.";
    return;
  }
  if (run.index === steps.length) {
    instruction.textContent = "Scenario complete. Did it work as expected? Add any feedback in Notes, or choose another scenario.";
    const other = [...scenarios.values()].filter(link => link !== scenario);
    nextScenario = other.find(link => progress(link) === "new") ||
      other.find(link => progress(link) !== "done");
    nextButton.hidden = !nextScenario;
    if (nextScenario) nextButton.textContent = nextScenario.textContent + " next scenario";
    feedback.hidden = true;
    return;
  }
  const action = screen.querySelector('[data-action="' + steps[run.index] + '"]');
  if (!action || action.closest("[hidden]")) {
    instruction.textContent = "This screen is missing the next action. Use Notes to describe the missing action.";
    return;
  }
  const row = action.closest(".action-row")?.querySelector("span");
  const edit = screen.querySelector("input[data-bind]");
  const prefix = edit ? "Try editing “" + edit.labels[0].textContent.trim() + "”, then select " : "Select ";
  instruction.textContent = prefix + "“" + action.textContent + "”" +
    (row ? " beside “" + row.textContent + "”" : "") + ".";
}

document.addEventListener("click", event => {
  const link = event.target.closest("a");
  if (!link || event.defaultPrevented || event.button !== 0 ||
      event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
  if (link.dataset.reveal) reveal(link.dataset.reveal);
  let screen = link.hash.slice(1);
  let run = history.state?.walkthrough;
  if (link.dataset.scenario) {
    const saved = record(link);
    if (progress(link) === "started" && document.getElementById(saved.run.screen)) {
      run = saved.run;
      screen = run.screen;
      for (const id of run.revealed || []) reveal(id);
    } else {
      run = {scenario: link.dataset.scenario, signature: link.dataset.signature, index: 0, screen};
    }
  } else if (link.dataset.action && scenarios.has(run?.scenario) &&
             run.signature === scenarios.get(run.scenario).dataset.signature && run.screen === page().id) {
    const steps = scenarios.get(run.scenario).dataset.steps.split(" ");
    if (run.index >= steps.length) return;
    const diverged = run.diverged || link.dataset.action !== steps[run.index];
    const revealed = Array.from(document.querySelectorAll("[data-after]:not([hidden])"),
      node => node.dataset.after);
    run = {...run, index: run.index + 1, screen, diverged, revealed};
  } else {
    return;
  }
  event.preventDefault();
  const totalSteps = scenarios.get(run.scenario).dataset.steps.split(" ").length;
  if (!run.diverged) remember(run, run.index === totalSteps);
  const destination = "#" + screen;
  if (location.hash === destination) {
    history.pushState({walkthrough: run}, "");
  } else {
    location.hash = destination;
    history.replaceState({walkthrough: run}, "");
  }
  describe();
  const title = page().querySelector("h1");
  title.tabIndex = -1;
  title.focus();
  window.scrollTo(0, 0);
});
window.addEventListener("popstate", describe);
window.addEventListener("hashchange", describe);
describe();

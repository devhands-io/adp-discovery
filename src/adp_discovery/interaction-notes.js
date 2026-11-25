// Keep each note independent so typing on one screen cannot replace another screen's note.
const noteModel = document.querySelector("main").dataset;
const notePrefix = "adp-notes:" + noteModel.model + ":" + noteModel.revision + ":";
const notesByKey = new Map();
const notePanels = new Map(Array.from(document.querySelectorAll("[data-notes-for]"),
  panel => [panel.dataset.notesFor, panel]));
const copyButton = document.getElementById("copy-notes");
const copyStatus = document.getElementById("copy-status");
const manualCopy = document.getElementById("manual-copy");
const screenNotes = document.getElementById("screen-notes");

function noteKey(note) {
  return JSON.stringify([note.scenario, note.screen || "", note.step || ""]);
}

try {
  for (const key of Object.keys(localStorage)) {
    if (key.startsWith(notePrefix)) notesByKey.set(key.slice(notePrefix.length), JSON.parse(localStorage[key]));
  }
} catch {
  // In a browser without storage, notes can still be written and copied during this visit.
}

function fieldFor(note, caption) {
  const label = document.createElement("label");
  label.textContent = caption;
  const field = document.createElement("textarea");
  const key = noteKey(note);
  field.dataset.noteKey = key;
  field.value = notesByKey.get(key)?.text || "";
  field.addEventListener("input", () => {
    const updated = {...note, text: field.value};
    const present = Boolean(field.value.trim());
    if (present) notesByKey.set(key, updated);
    else notesByKey.delete(key);
    copyStatus.textContent = "";
    manualCopy.hidden = true;
    try {
      if (present) localStorage.setItem(notePrefix + key, JSON.stringify(updated));
      else localStorage.removeItem(notePrefix + key);
    } catch {
      copyStatus.textContent = "Browser storage is unavailable. Copy your notes before closing this page.";
    }
    copyButton.disabled = !notesByKey.size;
  });
  label.append(field);
  return label;
}

function displayScenarioNotes(panel) {
  const sid = panel.dataset.notesFor;
  const fields = panel.querySelector(".note-fields");
  fields.replaceChildren(fieldFor({scenario: sid}, "Scenario notes"));
  for (const note of notesByKey.values()) {
    if (note.scenario === sid && note.screen) fields.append(fieldFor(note, note.context));
  }
}

for (const panel of notePanels.values()) {
  panel.addEventListener("toggle", () => {
    if (panel.open) displayScenarioNotes(panel);
  });
}

function displayScreenNote(run, screen) {
  screenNotes.hidden = !run;
  if (!run) {
    screenNotes.dataset.key = "";
    return;
  }
  const stepIds = scenarios.get(run.scenario).dataset.steps.split(" ");
  let step = "After final step";
  if (run.diverged) step = "Alternate route";
  else if (run.index < stepIds.length) step = "Step " + (run.index + 1) + " · " + stepIds[run.index];
  const context = screen.querySelector("h1").textContent + " · " + step;
  const note = {scenario: run.scenario, screen: screen.id, step, context};
  const key = noteKey(note);
  if (screenNotes.dataset.key !== key) {
    screenNotes.dataset.key = key;
    screenNotes.querySelector(".note-fields").replaceChildren(fieldFor(note, context));
  }
}

window.addEventListener("storage", event => {
  if (!event.key?.startsWith(notePrefix)) return;
  const key = event.key.slice(notePrefix.length);
  const updated = event.newValue && JSON.parse(event.newValue);
  if (updated) notesByKey.set(key, updated);
  else notesByKey.delete(key);
  copyButton.disabled = !notesByKey.size;
  for (const field of document.querySelectorAll("[data-note-key]")) {
    if (field.dataset.noteKey === key && field !== document.activeElement) field.value = updated?.text || "";
  }
});

function exportNotes() {
  const lines = [document.title, "Model revision " + noteModel.revision];
  for (const [sid, link] of scenarios) {
    const notes = [...notesByKey.values()].filter(note => note.scenario === sid);
    if (!notes.length) continue;
    lines.push("", link.closest(".scenario").querySelector("h3").textContent + " [" + sid + "]");
    for (const note of notes) {
      if (note.screen) lines.push(note.context + " (#" + note.screen + ")");
      lines.push(note.text, "");
    }
  }
  return lines.join("\n").trimEnd();
}

copyButton.disabled = !notesByKey.size;
copyButton.addEventListener("click", async () => {
  const output = exportNotes();
  try {
    await navigator.clipboard.writeText(output);
    manualCopy.hidden = true;
    copyStatus.textContent = "Notes copied. Paste them into chat.";
  } catch {
    manualCopy.value = output;
    manualCopy.hidden = false;
    manualCopy.focus();
    manualCopy.select();
    copyStatus.textContent = "Copy the selected notes and paste them into chat.";
  }
});

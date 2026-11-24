# adp-discovery

- Keep the discovery core product-agnostic. Put domain questions and overlay
  applicability in the catalog.
- Use the interview skill's instructions for reasoning and stakeholder
  interaction. Use Python for deterministic composition, validation,
  persistence, and reporting.
- Keep working JSON state separate from generated artifacts. Use stable
  lowercase kebab-case IDs and preserve evidence and confirmed decision history.
- Validate with `python -m src.adp_discovery validate` and
  `python -m unittest discover -s tests -v` from the repository root.
- When running commands from a fresh agent session, use the project virtual
  environment's interpreter directly if it exists (`.venv/bin/python` on
  macOS and Linux, `.venv\Scripts\python.exe` on Windows).
- Update the architecture and decision log when changing a documented contract.
  Update the pilot or acceptance tests when changing observable behavior.
- Keep changes scoped to the requested Discovery work and the current slice.

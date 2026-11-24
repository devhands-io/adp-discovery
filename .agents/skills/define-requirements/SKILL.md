---
name: define-requirements
description: Derive traceable product requirements and verifiable acceptance criteria from confirmed discovery findings.
---

# Define requirements

Load the [shared discovery workspace](../../../docs/supporting-skills.md).
Read the saved requirements in v3 or the existing `requirements.md` in
v1 and v2 before assigning IDs.

1. Derive requirements from confirmed decisions and verified findings that
   establish an applicable obligation. Cite the supporting decision and
   evidence IDs where available. Treat preferences, proposals, assumptions,
   and disputed sources as review inputs. If support is missing, record the
   gap and leave the affected requirement pending.
2. Group requirements by applicable category, such as functional, quality,
   operational, regulatory, or other constraints. State one outcome or
   constraint per requirement and give it a stable `req-` ID. Reuse IDs for
   unchanged obligations. If an obligation is replaced, give its replacement a
   new ID and retain the predecessor and its source links as superseded.
3. Describe how to verify each requirement using an observable outcome,
   conditions, and a threshold or example when supported. Carry over the
   confirmed trigger and level of obligation. If sources differ on whether a
   behavior is required or permitted, flag the difference and identify what
   can still be verified. Leave unconfirmed targets and design choices open.
4. Save gaps and contradictions in the ledger. In v3, save requirements and
   their stable acceptance criterion IDs in `discovery.requirements`. Link
   active obligations to confirmed decisions and those decisions to supported
   findings. Record known requirement impacts on questions and risks. Generate
   the baseline from the saved revision, which flags stale or weak support.
   In v1 and v2, record each ID, obligation, sources, and verification gap or
   acceptance criteria in `requirements.md`.

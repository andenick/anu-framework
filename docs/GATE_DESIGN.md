# Gate Design

How the Anu Framework's automated gates are built, and the rules an
exemption has to satisfy before it is allowed to exist.

This document is cited by name and section from shipped code —
`skills/anu-publish/audit.py`, `skills/anu-publish/generate_publish_package.py`
and `skills/anu-publish/SKILL.md` all reference §6(a), §6(b) and §6(c).
Those citations are the reason this file exists; the numbering below is
therefore stable and must not be renumbered.

---

## 1. What counts as a gate

A gate is an automated check whose failure **stops something**: a stage
advance, a package build, a CI run, a publish. Three properties make it a
gate rather than a report:

1. It runs without being asked — in CI, or as a mandatory step of the
   command it guards.
2. It has a non-zero exit path that callers honour.
3. It is capable of failing on the tree it is run against.

A check that can only ever print "OK" is documentation, not a gate.

The framework's gates:

| Gate | Implementation | Guards |
|---|---|---|
| Framework self-audit (D01–D19) | `tools/check_framework.py` → `skills/anu-doctor/check_framework.py` | Internal consistency of the framework itself; runs in CI on every push and PR |
| Project self-audit (P01–P39) | `skills/anu-doctor/check_project.py` | A single data project's internal consistency |
| Pre-publication scrub | `skills/anu-publish/audit.py`, wrapped by `tools/audit_publish.py` | Internal references leaking into a public release |
| Package gates (P01–P15) | `skills/anu-publish/generate_publish_package.py` | The contents of a publish package |
| Stage acceptance gates | `skills/anu-build/lib/stage_runner.py` (`check_gate`) | Advancing from one build stage to the next |

---

## 2. Severity is a two-value decision

Every check declares `FAIL` or `WARN`, and the distinction is about
consequence, not confidence:

- **FAIL** — the condition makes the artifact wrong or unsafe to ship.
  Exit non-zero. `check_framework.py` returns 1 if any FAIL-severity check
  fails, regardless of how many WARNs there are.
- **WARN** — the condition is worth a human's attention but does not make
  the artifact wrong. It is printed in full, never hidden, and never
  aggregated into a score.

There is no third level. "Info", "nit" and "advisory" tiers exist to let
findings accumulate unread, which is the failure mode this document is
written against.

A check may be promoted WARN → FAIL when evidence shows the condition
does ship real defects. `anu-publish` P10/P11 were promoted in v2.1 after
workspace paths reached a public site.

---

## 3. An unarmed gate must announce itself

A gate that has nothing to check against must report that fact rather
than reporting success. Reporting CLEAN because the deny-list is empty is
the same outcome as reporting CLEAN because the tree is clean, and the
two are not the same fact.

Two shipped examples:

- `audit.py` treats an empty effective deny-list as a hard error, not as
  a clean run.
- `generate_publish_package.py` emits `P11_NO_INTERNAL_REFS: WARN — NOT
  ENFORCED` when no organization deny-list is configured, so an unarmed
  gate is visible in the report instead of silently green.

---

## 4. Gates carry self-tests

A gate whose matching logic can silently stop matching needs a test that
proves it still bites. `audit.py --self-test` runs the effective patterns
against built-in positive fixtures (strings that must be caught) and
negative fixtures (strings that must not be), and fails if either
misbehaves. Run it in CI alongside the audit itself — see §6(c).

---

## 5. Findings are listed, never suppressed

When a gate is failing, the correct response is to fix the finding or to
record an exemption under §6. It is never to remove the finding from the
gate's view.

The concrete precedent in this repository: `anu-publish` supports an
optional `.publish_ignore` exclusion file. This repository shipped one
that exempted eleven files — including every file that carried a leak, so
the gate reported clean while the leaks were still there. The file was
deleted rather than shortened, and the findings it had been hiding were
then either fixed or the offending documents withdrawn. This repository
ships no `.publish_ignore`, deliberately.

A green result obtained by exempting the failing files is worse than a
red one, because it also destroys the signal.

---

## 6. Exemptions

An exemption is a deliberate, recorded decision that a specific finding
will not be fixed. It is a normal and legitimate thing to have. It is
also the mechanism by which gates rot, so it carries a fixed shape.

### 6(a) — Every exemption is a committed, reviewable line

An exemption must be:

1. **Committed** — it lives in a tracked file, so it appears in the diff
   of the commit that introduces it and can be argued with in review.
   Never a runtime flag, an environment variable, or a silent skip.
2. **Attributed** — it records three fields:
   - `reason` — why this finding will not be fixed, in specific terms.
     "Known issue" and "false positive" are not reasons; "the checker
     resolves scripts against the skill root and this one ships under
     `scripts/`" is.
   - `owner` — the person or role answerable for it.
   - `review_by` — a date. An exemption without an expiry is a permanent
     silent skip wearing a comment.
3. **Narrow** — it names the specific check and the specific file or
   finding. A pattern that exempts a whole directory is not an exemption,
   it is a hole.

Recommended form, whether in a `.publish_ignore`, a config file, or a
code comment beside a hard-coded skip:

```
# EXEMPTION: D10 / skills/example/SKILL.md
# reason:    <specific, falsifiable statement of why this cannot be fixed now>
# owner:     <name or role>
# review_by: YYYY-MM-DD
```

**The exemption register.** This repository currently records **no
exemptions**. `python tools/check_framework.py` exits 0 with zero
FAIL-severity failures and zero warnings; `python skills/anu-publish/audit.py`
reports CLEAN with no `.publish_ignore` present and only the §6(b)
self-exemption in force. If that ever stops being true, the exemptions
belong here, in this section, in the form above.

### 6(b) — The narrow self-exemption

A gate that scans text and is itself defined in text will match itself.
`audit.py` carries the positive fixtures it tests against, and the
deny-list files carry the patterns. Both would fail their own scan.

The permitted resolution is a self-exemption that is:

- **hard-coded**, so it appears in the source and cannot be widened by
  configuration;
- limited to *the gate and its own definition* — in this repository
  exactly three paths: `anu-publish/audit.py`,
  `anu-publish/scrub_patterns.json`, and the private overlay filename;
- accompanied by a comment saying that nothing else is exempt.

This is the only category of exemption that does not need §6(a)'s
`review_by`, because it is structural rather than circumstantial: the gate
will always contain its own patterns.

### 6(c) — A gate that cannot fail is not a gate

Before trusting a green result, establish that a red one was reachable.
Practically:

- Ship a self-test that proves the matcher still matches (§4).
- Treat an empty rule set as an error, not as a pass (§3).
- When a gate goes green after a change, confirm it went green because
  the findings were fixed — not because the input set shrank, the
  patterns stopped loading, or the failing files were excluded.

A green badge whose red state is unreachable is a claim about the tooling,
not about the code.

---

## 7. Reporting a standing failure honestly

Where a gate has failures that are neither fixed nor exempted — work in
progress, not a decision — say so where readers will see it, with the
count and the reason per check. `README.md` carries a "Current self-audit
state" section for exactly this. Listing the failures is not an admission
of sloppiness; hiding them is.

---

*Part of the Anu Framework v12.2.*

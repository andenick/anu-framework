# Contributing to the Anu Framework

Thanks for your interest. A few guidelines.

## Reporting issues

Open a GitHub issue. Include:

- Which skill is affected (`anu-X`)
- What you expected vs what happened
- Repro steps
- Output of `python tools/check_framework.py` if relevant

## Proposing changes

### To a skill

1. Open an issue describing the change first.
2. Update the skill's `SKILL.md`:
   - Bump the frontmatter `version:` field
   - Update the body headline `# Anu <Name> Standard vN.N` to match
   - Add an entry to the `## Version History` section
3. Update `docs/SKILL_VERSION_MATRIX.md` and `docs/ANU_FRAMEWORK_OVERVIEW.md`
   if the version changed.
4. Update `docs/ANU_FRAMEWORK_CHANGELOG.md` for any framework-level effect.
5. Run `python tools/check_framework.py` — must be CLEAN.
6. Open the PR.

### Adding a new skill

1. Open an issue first; new skills change the framework's surface.
2. Create `skills/anu-X/SKILL.md` with full frontmatter (`name`, `version`,
   `description`, `when-to-use`, `search-hints`, `allowed-tools`,
   `argument-hint`, `requires`, `part-of`).
3. Body must include: Overview table, Purpose, Commands, When to run,
   Integration with Anu Framework, Documentation Contract, Version History,
   Canonical references, footer.
4. Add a row to the version matrix AND overview tables — the framework
   version must bump (e.g., 20 → 21 skills means v11.0 → v12.0).
5. `anu-doctor` will refuse to pass until all cross-references resolve.

### Removing or archiving a skill

1. Rename folder to `anu-X-archived-YYYYMMDD/` (preserved for history).
2. Remove from MATRIX, OVERVIEW, and any `requires:` references.
3. CHANGELOG entry describing the deprecation.

## Local development

```bash
git clone https://github.com/andenick/anu-framework
cd anu-framework
python tools/check_framework.py
```

No Python dependencies required for the check — it's stdlib-only.

## Style

- SKILL.md frontmatter keys: `name`, `version`, `description`, `when-to-use`,
  `search-hints`, `allowed-tools`, `argument-hint`, `requires`, `part-of`
- Body headline format: `# Anu <Name> Standard vN.N` (exactly matches
  frontmatter `version:`)
- Version History uses `- **vN.N** (Month YYYY) — change description`
- Cross-skill references use lowercase IDs (`anu-research`, not `Anu Research`)
  except in the per-skill display table

## CI

Every PR runs:

- `python tools/check_framework.py` — framework consistency (must be CLEAN)
- `python tools/audit_publish.py --strict` — no internal-reference leaks

PRs that fail CI cannot merge. Don't bypass; fix the underlying issue.

## License

By contributing, you agree your contributions are MIT-licensed (same as the
project).

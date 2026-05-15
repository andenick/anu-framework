# Porting Log — {{ PROJECT_NAME }}

For each predecessor series, the agent decides one of four port modes during
Wave W.1 (research mining). This log records every decision.

## Port modes

- **`verbatim`** — predecessor research is accurate and complete; SID find-
  and-replace is the only edit
- **`rewrite`** — predecessor research is partly accurate but needs editing
  (methodology changed, missed sources added, errors corrected)
- **`re-mine`** — predecessor research is too sparse / wrong / built against
  a different KB; discard and follow the fresh-mine procedure
- **`dropped`** — predecessor series not carried into the rebuild (crosswalk
  has blank `new_id` or status `dropped`)

## Decisions

| new_id | old_id | mode | reason |
|---|---|---|---|
| D001 | T001 | verbatim | Book methodology unchanged; only SID rewrites needed |
| D007 | T007 | rewrite | Predecessor missed Appendix B-3 methodology; added |
| D012 | T012 | re-mine | Predecessor research was 80% empty; needed fresh KB pass |
| AD1001 | N1001 | verbatim | External study; predecessor's research is solid |
| _(dropped)_ | T099 | dropped | Placeholder in predecessor; no actual series |
| D015 | T015 | _(deferred)_ | Need user input on whether to carry this forward |

## Acceptance

- [ ] Every crosswalk row with `status: confirmed` and non-blank `new_id`
      has a port-mode entry here.
- [ ] Every research JSON at `Technical/research/<new_id>_research.json` has
      `ported_from`, `ported_at`, `port_mode` metadata if it was ported.
- [ ] `anu-doctor project` P03 (research-JSON ↔ registry alignment) PASSes.

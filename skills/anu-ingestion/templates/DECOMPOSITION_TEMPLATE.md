# {{ SERIES_ID }} — {{ SERIES_NAME }} — Decomposition

Composite series only. Documents how this series is built from subsources.
Direct (single-source) series do not have a decomposition file.

---

## Structure

```mermaid
graph TD
  A[{{SERIES_ID}}-A<br/>Source A, <years>] --> X[{{SERIES_ID}}<br/>Final composite]
  B[{{SERIES_ID}}-B<br/>Source B, <years>] --> X
  C[{{SERIES_ID}}-EXT<br/>API extension, <years>] -.-> X
```

## Subsources

### `{{SERIES_ID}}-A` — <subsource A name>

- **Source**: <publication, table/series ID, URL>
- **Period**: <YYYY>-<YYYY>
- **Units**: <units>
- **Construction**: direct | derived from <source>
- **Notes**: <quality, vintage, anything noteworthy>

### `{{SERIES_ID}}-B` — <subsource B name>

(same fields)

## Splice methodology

- **Splice point year**: <YYYY>
- **Splice method**: growth-rate splice | direct splice | level splice
- **Rationale**: <why this method? what's the assumption?>
- **Predecessor's choice** (if applicable): <what the predecessor did, and
  whether we kept it; if not, log to DIVERGENCE_REGISTER>

## Combined series formula

```
{{SERIES_ID}}[t] =
    {{SERIES_ID}}-A[t]                                  for t <= 1958
    {{SERIES_ID}}-A[1958] * ({{SERIES_ID}}-B[t] /
                              {{SERIES_ID}}-B[1958])    for t > 1958
```

(adjust formula to match the actual construction; this is just an example
of the growth-rate-splice pattern)

## Validation

V03 validates the combined series against the book's published values. See
[`{{SERIES_ID}}_DPR.md`](./{{SERIES_ID}}_DPR.md) § Reference values for the
benchmark table.

# Anu Extenbook Data Sheet Template

## Sheet 1: Data

This template defines the structure for the Data sheet in an Anu Extenbook.

---

## Row Structure

### Row 0: Metadata Row

Column-specific source citations and metadata.

**Format**:
```
| Year | [Source Citation A] | [Source Citation B] | [Source Citation C] | [Transform Desc] | [Transform Desc] | FINAL: S### Extended |
```

**Example**:
```
| Year | BEA LTEG Table A15 (1860-1959) | FRB G.17 (1919-2010) | FRED INDPRO (2011-2025) | Rebased to 1958=100 | Growth Rate Splice @1919,@2010 | FINAL: S001 Extended |
```

**Styling**:
- Background: #D9E2F3 (Light Blue)
- Font: Bold
- Text wrap: Yes

---

### Row 1: Headers

Descriptive column names with subsource IDs.

**Format**:
```
| Year | S###A: [Source] ([Period]) | S###B: [Source] ([Period]) | S###C: [Source] ([Period]) | Rebased | Spliced | S###_FINAL |
```

**Example**:
```
| Year | S001A: BEA (1860-1959) | S001B: FRB (1919-2010) | S001C: FRED (2011-2025) | Rebased | Spliced | S001_FINAL |
```

**Styling**:
- Background: #4472C4 (Blue)
- Font: White, Bold
- Row height: 25

---

### Row 2+: Data Rows

Year-indexed values with appropriate NaN for out-of-range periods.

**Example**:
```
| 1860 | 2.3  | NaN  | NaN  | 2.8  | 2.8  | 2.8  |
| 1861 | 2.5  | NaN  | NaN  | 3.0  | 3.0  | 3.0  |
| ...  |      |      |      |      |      |      |
| 1919 | 15.2 | 15.4 | NaN  | 16.5 | 16.5 | 16.5 |  <- Splice point
| ...  |      |      |      |      |      |      |
| 2010 | NaN  | 95.2 | 95.3 | 100  | 100  | 100  |  <- Modern splice
| 2011 | NaN  | NaN  | 96.1 | NaN  | 101.2| 101.2|
```

---

## Column Structure

### Column A: Year

| Property | Value |
|----------|-------|
| Header | Year |
| Format | Integer |
| Width | 8 |
| Color | White background |

---

### Columns B-N: Subsources

Each subsource gets its own column.

| Property | Value |
|----------|-------|
| Header | S###X: [Source] ([Period]) |
| Format | Number, 2 decimal places |
| Width | 15-20 |
| Color (Original) | #FFF2CC (Light Yellow) |
| Color (Extension) | #E6F2FF (Light Blue) |
| NaN Display | Empty cell with #F2F2F2 background |

**Subsource Column Order**:
1. Original subsources in chronological order (A, B, C...)
2. Extension subsources last

---

### Columns O+: Transformations

Intermediate calculation columns.

| Property | Value |
|----------|-------|
| Header | [Transformation Name] |
| Format | Number, 2-4 decimal places |
| Width | 15 |
| Color | #FCE4D6 (Light Orange) |
| Cell Comments | Include formula used |

**Common Transformations**:
- Rebased (to common base year)
- Spliced (growth rate or level splice)
- Indexed (reindexed to specific year)
- Adjusted (seasonal, inflation, etc.)

---

### Last Column: FINAL

The final extended series.

| Property | Value |
|----------|-------|
| Header | S###_FINAL |
| Format | Number, 2 decimal places |
| Width | 15 |
| Color | #E6FFE6 (Light Green) |
| Border | Right border thick |

---

## Splice Point Highlighting

Rows where splicing occurs get special highlighting.

| Property | Value |
|----------|-------|
| Row Background | #FFFF00 (Yellow) |
| Row Border | Top and bottom borders |
| Cell Comment | "Splice point: [Description]" |

**Example Splice Years**:
- 1919: Historical to modern splice
- 2010: Original to extension splice

---

## Cell Formatting

### Numbers

| Type | Format |
|------|--------|
| Index values | `#,##0.00` |
| Percentages | `0.00%` |
| Large numbers | `#,##0` |
| Very small | `0.0000` |

### Empty Cells (NaN)

| Property | Value |
|----------|-------|
| Display | Empty (no text) |
| Background | #F2F2F2 (Light Gray) |

### Cell Comments

Add comments to transformation columns showing formulas:

```
=S001A * (100 / S001A[1958])
```

---

## Column Widths

| Column Type | Width |
|-------------|-------|
| Year | 8 |
| Subsources | 18 |
| Transformations | 15 |
| Final | 15 |

---

## Conditional Formatting

### Active Data Range

For each subsource column, highlight the active year range:

- Years within subsource period: Normal color
- Years outside subsource period: #F2F2F2 (grayed)

### Value Validation

- Values within expected range: Normal
- Values outside expected range: Red font

---

## Freeze Panes

Freeze at Row 2, Column B:
- Row 0-1 (metadata and headers) always visible
- Column A (Year) always visible

---

## Example Complete Layout

```
     A          B                    C                    D                    E          F           G
0  | Year     | BEA LTEG A15       | FRB G.17           | FRED INDPRO        | Rebased   | Spliced   | FINAL: S001 |
1  | Year     | S001A: BEA         | S001B: FRB         | S001C: FRED        | 1958=100  | Growth    | S001_FINAL  |
   |          | (1860-1959)        | (1919-2010)        | (2011-2025)        |           | Splice    |             |
2  | 1860     | 2.3                |                    |                    | 2.8       | 2.8       | 2.8         |
3  | 1861     | 2.5                |                    |                    | 3.0       | 3.0       | 3.0         |
...
60 | 1919     | 15.2               | 15.4               |                    | 16.5      | 16.5      | 16.5        | <- Yellow
...
151| 2010     |                    | 95.2               | 95.3               | 100.0     | 100.0     | 100.0       | <- Yellow
152| 2011     |                    |                    | 96.1               |           | 101.2     | 101.2       |
...
166| 2025     |                    |                    | 105.7              |           | 111.2     | 111.2       |
```

---

*Template Version 1.0 - Anu Extenbook Standard*

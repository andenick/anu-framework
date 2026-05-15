#!/usr/bin/env python3
"""
P{NN} - Process {SERIES_NAME} ({SERIES_ID})

Loads {SOURCE_TABLE} parsed data, {BRIEF_DESCRIPTION}.
Figures: {FIGURE_LIST}

Depends on: {DEPENDENCY_LIST}
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
from lib.paths import ensure_dirs, SERIES_OUT, CHOPPED_OUT, EXTENBOOKS
from lib.data_io import load_parsed
from lib.config_loader import load_registry
from lib.registry_reader import get_series, get_research
from lib.formats.chopped_writer import write_chopped
from lib.formats.extenbook_writer import write_extenbook

SERIES_ID = "{SERIES_ID}"
SOURCE_TABLE = "{SOURCE_TABLE_ID}"


def process():
    """Process {SERIES_ID}: load source data, compute series, write all outputs."""
    ensure_dirs()
    registry = load_registry()
    series_config = get_series(registry, SERIES_ID)

    # 1. Load source data
    df, src_path = load_parsed(SOURCE_TABLE)
    steps = [f"Loaded {SOURCE_TABLE} from {src_path} ({len(df)} rows)"]

    # 2. Construct the series
    # TODO: Implement series-specific construction logic
    # result_series = pd.Series(...)
    # steps.append("Computed ...")

    # 3. Build data_dict (REQUIRED — consumed by visualization export)
    data_dict = {
        # "{SERIES_ID}-A": result_series,
    }

    # 4. Write outputs
    outputs = []

    final_path = SERIES_OUT / f"{SERIES_ID}_final.csv"
    # TODO: Write final CSV
    # final_df.to_csv(final_path)
    outputs.append(str(final_path))

    write_chopped(data_dict, registry, SERIES_ID, CHOPPED_OUT)
    outputs.append(str(CHOPPED_OUT / f"{SERIES_ID}_chopped.csv"))

    research_data = get_research(SERIES_ID)
    write_extenbook(data_dict, registry, research_data, SERIES_ID, EXTENBOOKS)
    outputs.append(str(EXTENBOOKS / f"{SERIES_ID}_extenbook.xlsx"))

    # 5. Build result
    result = {
        "series_id": SERIES_ID,
        "status": "SUCCESS",
        "steps": steps,
        "data_dict": data_dict,
        "validation": {
            "expected_range": series_config.get("validation", {}).get("expected_range"),
        },
        "outputs": outputs,
    }

    return result


if __name__ == "__main__":
    import pprint
    result = process()
    pprint.pprint({k: v for k, v in result.items() if k != "data_dict"})

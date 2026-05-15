#!/usr/bin/env python3
"""
L{NN} - Load {SERIES_NAME} ({SERIES_ID}, {SOURCE_DESCRIPTION})

Parses the Chopped CSV and writes S###_parsed.csv to raw-data/parsed/.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from lib.data_io import load_chopped_table

SERIES_ID = "{SERIES_ID}"
SOURCE_FILE = "ch{NN}/{FILENAME}.csv"


def load():
    """Load {SERIES_ID} data: parse Chopped CSV into parsed format."""
    return load_chopped_table(SERIES_ID, SOURCE_FILE, "L{NN}")


if __name__ == "__main__":
    load()

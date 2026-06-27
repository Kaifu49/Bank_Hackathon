"""
delimited_reader — robust, ragged-tolerant reader for CSV/TXT statement files.

pandas' parser enforces a consistent column count and crashes on real bank CSVs
that have a metadata preamble with a different number of delimiters than the
transaction rows (e.g. "Expected 4 fields in line 3, saw 9"). The Python csv
module does NOT enforce column counts, so we use it and pad rows to a common
width, producing a clean grid for TabularReader.
"""

from __future__ import annotations

import csv
import io


_CANDIDATES = [",", "\t", "|", ";"]


def _detect_delimiter(lines: list[str]) -> str:
    sample = [ln for ln in lines if ln.strip()][:50]
    best, best_score = ",", -1
    for delim in _CANDIDATES:
        counts = [ln.count(delim) for ln in sample]
        # score = how many lines contain it * its typical count
        present = [c for c in counts if c > 0]
        if not present:
            continue
        # median-ish: most common positive count, weighted by coverage
        typical = max(set(present), key=present.count)
        score = len(present) * typical
        if score > best_score:
            best, best_score = delim, score
    return best


def read_grid(file_path: str) -> list[list[str]]:
    """Read a delimited file into a padded 2-D grid of strings (ragged-safe)."""
    with open(file_path, encoding="utf-8", errors="replace", newline="") as fh:
        text = fh.read()

    lines = text.splitlines()
    if not lines:
        return []

    delimiter = _detect_delimiter(lines)

    reader = csv.reader(io.StringIO(text), delimiter=delimiter)
    rows = [[(c if c is not None else "").strip() for c in row] for row in reader]
    rows = [r for r in rows if any(cell != "" for cell in r)]
    if not rows:
        return []

    width = max(len(r) for r in rows)
    return [r + [""] * (width - len(r)) for r in rows]

"""Ingest: check every figure's evidence quote against its source markdown, then write dataset.json.

Two input paths, same checks:
  1. data/figures.csv, transcribed by hand (the fallback path, always available).
  2. ```figures fenced blocks inside the pull markdown files (read directly).

Structured block format (one per markdown file, or several):

    ```figures
    id,label,value,unit,kind,snapshot,as_of,source_name,source_url,evidence_quote,notes
    twitch_peak_nov19,GTA VI peak Twitch viewers,"6.2M",count,measured,launchday,2026-11-19,TwitchTracker,https://twitchtracker.com/games/...,"peak of 6.2M concurrent viewers",
    ```

The header is the figures.csv header minus evidence_file (implied: the file the block is in).
The evidence_quote must appear word for word in that file OUTSIDE the figures blocks, so a
block can never vouch for itself. An id defined twice (CSV vs block, or two blocks) is an error.
"""
import csv
import io
import os
import re

from .dataset import FIELDS, validate_rows, write_dataset
from .errors import EvidenceError, MissingInputError

_BLOCK = re.compile(r"^```figures[ \t]*\n(.*?)^```[ \t]*$", re.S | re.M)
BLOCK_FIELDS = tuple(f for f in FIELDS if f != "evidence_file")


def _norm(text):
    return re.sub(r"\s+", " ", text).strip()


def strip_figures_blocks(text):
    return _BLOCK.sub("", text)


def read_figures_blocks(md_path, root):
    """Return raw rows from every ```figures block in ``md_path`` (evidence_file filled in)."""
    with open(md_path, encoding="utf-8") as fh:
        text = fh.read()
    rel = os.path.relpath(md_path, root)
    rows = []
    for n, m in enumerate(_BLOCK.finditer(text), 1):
        reader = csv.DictReader(io.StringIO(m.group(1)))
        missing = [f for f in BLOCK_FIELDS if f not in (reader.fieldnames or [])]
        if missing:
            raise MissingInputError(f"{rel}: figures block {n} missing columns {missing}")
        for i, row in enumerate(reader):
            row = dict(row, evidence_file=rel, _origin=f"{rel}#figures{n}:{i + 2}")
            rows.append(row)
    return rows


def check_evidence(dataset, root):
    """Each quote must appear word for word (whitespace-insensitive) in its evidence file."""
    problems, cache = [], {}
    root_abs = os.path.realpath(root)
    for rid, fig in dataset.items():
        path = os.path.realpath(os.path.join(root, fig["evidence_file"]))
        if not path.startswith(root_abs + os.sep):
            problems.append(f"{rid}: evidence_file {fig['evidence_file']!r} is outside the project")
            continue
        if path not in cache:
            if not os.path.isfile(path):
                cache[path] = None
            else:
                with open(path, encoding="utf-8") as fh:
                    cache[path] = _norm(strip_figures_blocks(fh.read()))
        body = cache[path]
        if body is None:
            problems.append(f"{rid}: evidence_file {fig['evidence_file']!r} does not exist")
        elif _norm(fig["evidence_quote"]) not in body:
            problems.append(f"{rid}: evidence_quote not found word for word in {fig['evidence_file']}: "
                            f"{fig['evidence_quote']!r}")
    if problems:
        raise EvidenceError("evidence check failed:\n  " + "\n  ".join(problems))


def ingest(figures_csv, root, out_json, block_files=()):
    """Run the whole ingest. Returns the checked dataset; writes ``out_json`` only on success."""
    from .dataset import read_csv
    rows = read_csv(figures_csv) if figures_csv else []
    for md in block_files:
        rows.extend(read_figures_blocks(md, root))
    dataset = validate_rows(rows)
    check_evidence(dataset, root)
    if out_json:
        write_dataset(dataset, out_json)
    return dataset

"""Load and check figures (figures.csv rows and ```figures blocks); write data/dataset.json.

There are no default values anywhere: an empty required field is an error.
All problems are collected and reported in one go.
"""
import csv
import datetime
import json
import re

from .errors import MissingInputError, ParseError
from .parse import UNITS, parse_number

FIELDS = (
    "id", "label", "value", "unit", "kind", "snapshot", "as_of",
    "source_name", "source_url", "evidence_file", "evidence_quote", "notes",
)
REQUIRED = tuple(f for f in FIELDS if f not in ("notes", "source_url"))
KINDS = ("measured", "survey", "estimate", "proxy", "claim", "benchmark", "precedent")
SNAPSHOTS = ("baseline", "launchday", "reference")
NO_URL_PREFIX = "no URL:"  # e.g. "no URL: survey press release, no URL"
_SLUG = re.compile(r"^[a-z][a-z0-9_]*$")


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        missing_cols = [f for f in FIELDS if f not in (reader.fieldnames or [])]
        if missing_cols:
            raise MissingInputError(f"{path}: missing columns {missing_cols}")
        return [dict(row, _origin=f"{path}:{i + 2}") for i, row in enumerate(reader)]


def validate_rows(rows):
    """Validate raw rows; return {id: figure}. Raises MissingInputError listing every problem."""
    problems, out = [], {}
    for row in rows:
        where = row.get("_origin", "?")
        rid = (row.get("id") or "").strip()
        for f in REQUIRED:
            if not (row.get(f) or "").strip():
                problems.append(f"{where}: {rid or '<no id>'}: required field '{f}' is empty")
        if rid and not _SLUG.match(rid):
            problems.append(f"{where}: id {rid!r} is not a lowercase slug")
        if rid in out:
            problems.append(f"{where}: duplicate id {rid!r} (first at {out[rid]['_origin']})")
        unit = (row.get("unit") or "").strip()
        kind = (row.get("kind") or "").strip()
        snap = (row.get("snapshot") or "").strip()
        if unit and unit not in UNITS:
            problems.append(f"{where}: {rid}: unit {unit!r} not in {UNITS}")
        if kind and kind not in KINDS:
            problems.append(f"{where}: {rid}: kind {kind!r} not in {KINDS}")
        if snap and snap not in SNAPSHOTS:
            problems.append(f"{where}: {rid}: snapshot {snap!r} not in {SNAPSHOTS}")
        url = (row.get("source_url") or "").strip()
        if not url:
            problems.append(f"{where}: {rid}: source_url empty (use '{NO_URL_PREFIX} <reason>' if there is none)")
        elif not (url.startswith("http://") or url.startswith("https://") or url.startswith(NO_URL_PREFIX)):
            problems.append(f"{where}: {rid}: source_url {url!r} is neither a URL nor '{NO_URL_PREFIX} <reason>'")
        as_of = (row.get("as_of") or "").strip()
        if as_of:
            try:
                datetime.date.fromisoformat(as_of)
            except ValueError:
                problems.append(f"{where}: {rid}: as_of {as_of!r} is not YYYY-MM-DD")
        value = None
        if (row.get("value") or "").strip() and unit in UNITS:
            try:
                value = parse_number(row["value"], unit)
            except ParseError as exc:
                problems.append(f"{where}: {rid}: {exc}")
        if rid and rid not in out:
            fig = {f: (row.get(f) or "").strip() for f in FIELDS}
            fig["raw_value"] = fig.pop("value")
            fig["value"] = value
            fig["_origin"] = where
            out[rid] = fig
    if problems:
        raise MissingInputError("figure validation failed:\n  " + "\n  ".join(problems))
    return out


def write_dataset(dataset, path):
    clean = {k: {f: v for f, v in fig.items() if f != "_origin"} for k, fig in sorted(dataset.items())}
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(clean, fh, indent=2, sort_keys=True)
        fh.write("\n")


def load_dataset(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)

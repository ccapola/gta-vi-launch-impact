"""Shared test helpers. Tests use fixtures only; real data never enters a test."""
import csv
import json
import os
import shutil
import sys
import tempfile

TESTS = os.path.dirname(os.path.abspath(__file__))
PIPELINE = os.path.dirname(TESTS)
sys.path.insert(0, PIPELINE)

FIXTURES = os.path.join(TESTS, "fixtures")
CONFIG = os.path.join(PIPELINE, "config", "model_frozen.json")
MODEL = os.path.join(PIPELINE, "gta_audit", "model.py")

from gta_audit import freeze as fz  # noqa: E402
from gta_audit.ingest import ingest  # noqa: E402


def config():
    with open(CONFIG, encoding="utf-8") as fh:
        return json.load(fh)


def fixture_rows():
    with open(os.path.join(FIXTURES, "figures.csv"), newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


class Workspace:
    """A temp copy of the fixtures (so tests can edit figures / evidence freely)."""

    def __init__(self):
        self.dir = tempfile.mkdtemp(prefix="gta-test-")
        shutil.copy(os.path.join(FIXTURES, "evidence.md"), self.dir)
        self.csv = os.path.join(self.dir, "figures.csv")
        self.write_rows(fixture_rows())

    def write_rows(self, rows):
        with open(self.csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

    def ingest(self, block_files=()):
        return ingest(self.csv, self.dir, None, block_files=block_files)

    def lock(self):
        """Freeze copies of the real config + model (the real lock is never touched by tests)."""
        cfg = os.path.join(self.dir, "model_frozen.json")
        mdl = os.path.join(self.dir, "model.py")
        shutil.copy(CONFIG, cfg)
        shutil.copy(MODEL, mdl)
        lock_path = os.path.join(self.dir, "model_frozen.lock")
        return fz.freeze(cfg, mdl, lock_path), cfg, mdl, lock_path

    def cleanup(self):
        shutil.rmtree(self.dir, ignore_errors=True)

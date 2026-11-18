#!/usr/bin/env python3
"""GTA VI launch-impact pipeline CLI.

  run.py ingest                  check figures.csv (+ ```figures blocks) against evidence; write data/dataset.json
  run.py freeze                  lock config + model (refuses if already locked)
  run.py verify-freeze           check the lock hash
  run.py compute [--dry]         verify-freeze, compute results; --dry only reports section status
  run.py render [--allow-partial] [--out DIR]   verify-freeze, render HTML/PDF/PNGs
  run.py all [--allow-partial]   ingest, verify-freeze, compute, render

Any failure exits non-zero with the reason. Nothing is estimated to fill a gap.
"""
import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from gta_audit import freeze as fz  # noqa: E402
from gta_audit import model  # noqa: E402
from gta_audit.dataset import load_dataset  # noqa: E402
from gta_audit.errors import PipelineError  # noqa: E402
from gta_audit.ingest import ingest  # noqa: E402
from gta_audit.render import render  # noqa: E402

ROOT = os.path.dirname(HERE)
CONFIG = os.path.join(HERE, "config", "model_frozen.json")
LOCK = os.path.join(HERE, "config", "model_frozen.lock")
MODEL = os.path.join(HERE, "gta_audit", "model.py")
FIGURES = os.path.join(HERE, "data", "figures.csv")
DATASET = os.path.join(HERE, "data", "dataset.json")
RESULTS = os.path.join(HERE, "data", "results.json")
DATA_DIR = os.path.join(ROOT, "hidden_files", "data")
OUT = os.path.join(ROOT, "files", "report")


def _config():
    with open(CONFIG, encoding="utf-8") as fh:
        return json.load(fh)


def cmd_ingest(_):
    blocks = sorted(glob.glob(os.path.join(DATA_DIR, "*.md")))
    ds = ingest(FIGURES, ROOT, DATASET, block_files=blocks)
    print(f"ingest OK: {len(ds)} figures checked against evidence -> {os.path.relpath(DATASET, ROOT)}")


def cmd_freeze(_):
    lock = fz.freeze(CONFIG, MODEL, LOCK)
    print(f"frozen: {lock['locked_at_display']} · sha256 {lock['sha256'][:12]}")


def cmd_verify(_):
    lock = fz.verify(CONFIG, MODEL, LOCK)
    print(f"verify-freeze OK: locked {lock['locked_at_display']} · sha256 {lock['sha256'][:12]}")
    return lock


def cmd_compute(args):
    cmd_verify(args)
    cfg = _config()
    results = model.compute(cfg, load_dataset(DATASET))
    missing = model.core_missing(cfg, results)
    for sec in cfg["required_for_render"]:
        print(f"  {sec}: {'INCOMPLETE ' + str(missing[sec]) if sec in missing else 'complete'}")
    for group in ("anchors", "context", "proxies"):
        print(f"  {group}: present {sorted(results[group]['present'])}; missing {results[group]['missing']}")
    pre = results["benchmarks"]["precedent_gtav_2013"]
    print(f"  benchmarks.precedent_gtav_2013: {'rendered' if pre['rendered'] else 'omitted (no sourced row)'}")
    if args.dry:
        print("compute --dry: no results written")
        return
    model.require_core(cfg, results)
    with open(RESULTS, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2)
    print(f"compute OK -> {os.path.relpath(RESULTS, ROOT)}")


def cmd_render(args):
    lock = cmd_verify(args)
    cfg = _config()
    results = model.compute(cfg, load_dataset(DATASET))
    out = render(cfg, load_dataset(DATASET), results, lock, args.out, allow_partial=args.allow_partial)
    print(json.dumps(out, indent=2))


def cmd_all(args):
    cmd_ingest(args)
    args.dry = False
    cmd_compute(args)
    cmd_render(args)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("ingest").set_defaults(fn=cmd_ingest)
    sub.add_parser("freeze").set_defaults(fn=cmd_freeze)
    sub.add_parser("verify-freeze").set_defaults(fn=cmd_verify)
    c = sub.add_parser("compute")
    c.add_argument("--dry", action="store_true")
    c.set_defaults(fn=cmd_compute)
    for name, fn in (("render", cmd_render), ("all", cmd_all)):
        r = sub.add_parser(name)
        r.add_argument("--allow-partial", action="store_true")
        r.add_argument("--out", default=OUT)
        r.set_defaults(fn=fn)
    args = p.parse_args(argv)
    try:
        args.fn(args)
    except PipelineError as exc:
        print(f"STOP ({type(exc).__name__}): {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

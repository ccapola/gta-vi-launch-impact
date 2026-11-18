import inspect
import numbers
import unittest

from helpers import Workspace, config

from gta_audit import model
from gta_audit.errors import MissingInputError, SanityError


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.ws = Workspace()

    def tearDown(self):
        self.ws.cleanup()

    def test_claim_reproduction_420m(self):
        """REQUIRED: 1.5M workers x $280/day = $420M through the real ingest -> config -> model path."""
        ds = self.ws.ingest()
        self.assertEqual(ds["claim_workers"]["value"], 1_500_000)
        self.assertEqual(ds["claim_output_per_day"]["value"], 280)
        r = model.compute(config(), ds)
        self.assertEqual(r["claim_audit"]["status"], "complete")
        self.assertEqual(r["claim_audit"]["reproduced_usd"], 420_000_000)
        self.assertEqual(r["claim_audit"]["gap_usd"], 1_000_000_000 - 420_000_000)

    def test_claim_reproduction_mismatch_stops(self):
        with open(f"{self.ws.dir}/evidence.md", "a") as fh:
            fh.write("\nAltered claim: 1.5M workers at $300 per day.\n")
        rows = [dict(r, value="$300", evidence_quote="1.5M workers at $300 per day") if r["id"] == "claim_output_per_day" else r
                for r in self.ws_rows_with()]
        self.ws.write_rows(rows)
        with self.assertRaises(SanityError):
            model.compute(config(), self.ws.ingest())

    def ws_rows_with(self, **values):
        from helpers import fixture_rows
        return [dict(r, value=values[r["id"]]) if r["id"] in values else r for r in fixture_rows()]

    def test_no_numeric_defaults(self):
        for name, fn in inspect.getmembers(model, inspect.isfunction):
            if fn.__module__ != model.__name__:
                continue
            for p in inspect.signature(fn).parameters.values():
                self.assertFalse(
                    p.default is not inspect.Parameter.empty and isinstance(p.default, numbers.Number),
                    f"{name}({p.name}={p.default!r}) has a numeric default")

    def test_high_below_superbowl_cap(self):
        r = model.compute(config(), self.ws.ingest())
        self.assertLess(r["absence_cases"]["high"]["absences"], r["benchmarks"]["superbowl"]["absences"])
        self.assertEqual(r["benchmarks"]["superbowl"]["cap_check"], "passed")
        # and the build stops with an explanation when the cap is broken
        with open(f"{self.ws.dir}/evidence.md", "a") as fh:
            fh.write("\nAltered benchmark: 1M planned absences.\n")
        rows = [dict(r, value="1M", evidence_quote="1M planned absences") if r["id"] == "superbowl_monday_absences_2025" else r
                for r in self.ws_rows_with()]
        self.ws.write_rows(rows)
        with self.assertRaises(SanityError) as cm:
            model.compute(config(), self.ws.ingest())
        self.assertIn("sanity cap failed", str(cm.exception))

    def test_low_case_is_lift_on_absence_rate(self):
        r = model.compute(config(), self.ws.ingest())
        # 160M x 3% x 13%  (the +13% is a lift, never an absence rate)
        self.assertAlmostEqual(r["absence_cases"]["low"]["absences"], 160e6 * 0.03 * 0.13)
        self.assertAlmostEqual(r["output_per_worker_day"]["base"]["usd_per_day"], 280)
        self.assertAlmostEqual(r["benchmarks"]["superbowl"]["dollar_equivalent_usd"], 22.6e6 * 280)

    def test_missing_core_input_fails_loudly(self):
        rows = [r for r in self.ws_rows_with() if r["id"] != "us_employed"]
        self.ws.write_rows(rows)
        r = model.compute(config(), self.ws.ingest())
        self.assertEqual(r["absence_cases"]["low"]["status"], "insufficient")
        self.assertNotIn("absences", r["absence_cases"]["low"])
        with self.assertRaises(MissingInputError):
            model.require_core(config(), r)

    def test_precedent_omitted_without_source_row(self):
        r = model.compute(config(), self.ws.ingest())
        self.assertFalse(r["benchmarks"]["precedent_gtav_2013"]["rendered"])


if __name__ == "__main__":
    unittest.main()

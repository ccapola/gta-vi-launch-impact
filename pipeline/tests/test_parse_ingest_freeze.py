import os
import unittest

from helpers import Workspace, fixture_rows

from gta_audit import freeze as fz
from gta_audit.errors import EvidenceError, FreezeError, MissingInputError, ParseError
from gta_audit.parse import parse_number


class ParseTests(unittest.TestCase):
    def test_parse_units(self):
        self.assertEqual(parse_number("9.69M", "count"), 9_690_000)
        self.assertEqual(parse_number("$942M", "usd"), 942_000_000)
        self.assertAlmostEqual(parse_number("+13%", "pct"), 0.13)
        self.assertEqual(parse_number("1,530", "count"), 1530)
        self.assertEqual(parse_number("$1.54B", "usd"), 1_540_000_000)
        self.assertEqual(parse_number("$218.20", "usd_per_share"), 218.20)

    def test_parse_refuses_unclear(self):
        for bad, unit in (("~$280", "usd_per_day"), ("<1", "index"), ("$8.0–$8.2B", "usd"), ("13", "pct"),
                          ("1,53", "count"), ("12 million", "count"), ("", "count"), ("5%", "count"),
                          ("$5", "count"), ("about 5", "count")):
            with self.assertRaises(ParseError, msg=f"{bad!r} should be refused"):
                parse_number(bad, unit)


class IngestTests(unittest.TestCase):
    def setUp(self):
        self.ws = Workspace()

    def tearDown(self):
        self.ws.cleanup()

    def test_ingest_ok(self):
        self.assertEqual(len(self.ws.ingest()), len(fixture_rows()))

    def test_ingest_rejects_missing_quote(self):
        rows = fixture_rows()
        rows[0]["evidence_quote"] = "a sentence that is nowhere in the evidence file"
        self.ws.write_rows(rows)
        with self.assertRaises(EvidenceError) as cm:
            self.ws.ingest()
        self.assertIn(rows[0]["id"], str(cm.exception))

    def test_ingest_rejects_empty_required_field_and_duplicates(self):
        rows = fixture_rows()
        rows[1]["source_name"] = ""
        rows.append(dict(rows[2]))
        self.ws.write_rows(rows)
        with self.assertRaises(MissingInputError) as cm:
            self.ws.ingest()
        msg = str(cm.exception)
        self.assertIn("source_name", msg)
        self.assertIn("duplicate id", msg)

    def test_figures_block_read_directly(self):
        md = os.path.join(self.ws.dir, "launchday.md")
        with open(md, "w") as fh:
            fh.write("Peak viewers reached 6.2M on Twitch.\n\n```figures\n"
                     "id,label,value,unit,kind,snapshot,as_of,source_name,source_url,evidence_quote,notes\n"
                     "twitch_peak_nov19,Peak Twitch viewers,6.2M,count,measured,launchday,2026-11-19,"
                     "Fixture tracker,https://example.com/t,Peak viewers reached 6.2M,\n```\n")
        ds = self.ws.ingest(block_files=[md])
        self.assertEqual(ds["twitch_peak_nov19"]["value"], 6_200_000)
        self.assertEqual(ds["twitch_peak_nov19"]["evidence_file"], "launchday.md")

    def test_figures_block_cannot_vouch_for_itself(self):
        md = os.path.join(self.ws.dir, "launchday.md")
        with open(md, "w") as fh:
            fh.write("No prose here.\n\n```figures\n"
                     "id,label,value,unit,kind,snapshot,as_of,source_name,source_url,evidence_quote,notes\n"
                     "twitch_peak_nov19,Peak Twitch viewers,6.2M,count,measured,launchday,2026-11-19,"
                     "Fixture tracker,https://example.com/t,Peak Twitch viewers,\n```\n")
        with self.assertRaises(EvidenceError):
            self.ws.ingest(block_files=[md])


class FreezeTests(unittest.TestCase):
    def setUp(self):
        self.ws = Workspace()

    def tearDown(self):
        self.ws.cleanup()

    def test_freeze_tamper_detection(self):
        for target in ("config", "model"):
            lock, cfg, mdl, lock_path = self.ws.lock()
            self.assertEqual(fz.verify(cfg, mdl, lock_path)["sha256"], lock["sha256"])
            path = cfg if target == "config" else mdl
            with open(path, "a") as fh:
                fh.write("\n")
            with self.assertRaises(FreezeError, msg=f"edit to {target} not detected"):
                fz.verify(cfg, mdl, lock_path)
            os.remove(lock_path)

    def test_freeze_refuses_relock(self):
        _, cfg, mdl, lock_path = self.ws.lock()
        with self.assertRaises(FreezeError):
            fz.freeze(cfg, mdl, lock_path)

    def test_verify_without_lock_fails(self):
        with self.assertRaises(FreezeError):
            fz.verify(os.path.join(self.ws.dir, "x.json"), os.path.join(self.ws.dir, "y.py"),
                      os.path.join(self.ws.dir, "none.lock"))


if __name__ == "__main__":
    unittest.main()

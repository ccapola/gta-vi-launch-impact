import html
import os
import re
import struct
import unittest

from helpers import PIPELINE, Workspace, config

from gta_audit import model
from gta_audit.errors import MissingInputError
from gta_audit.render import build_html, find_chrome, fmt, pdf_page_count, render

TEMPLATE = os.path.join(PIPELINE, "templates", "report.html.tmpl")
NUM_TOKEN = re.compile(r"-?\$?\d[\d,.]*[KMBT%]?")


def body_text(page):
    page = re.sub(r"<style>.*?</style>", "", page, flags=re.S)
    return html.unescape(re.sub(r"<[^>]+>", " ", page))


def resolve(entry, ds, results, cfg, lock):
    """Re-derive an entry's text from its recorded provenance."""
    prov = entry["provenance"]
    if "dataset" in prov:
        fig = ds[prov["dataset"]]
        return fmt(fig["value"], fig["unit"]) if prov["field"] == "value" else fig[prov["field"]]
    if "results" in prov:
        node = results
        for part in prov["results"].split("."):
            node = node[part]
        if "id" in prov:
            assert prov["id"] in node, prov
            return prov["id"]
        return fmt(node, entry["unit"])
    if "config" in prov:
        node = cfg
        for part in prov["config"].split("."):
            node = node[part]
        return fmt(node["value"], entry["unit"])
    if "missing_input" in prov:
        assert prov["missing_input"] not in ds
        return prov["missing_input"]
    if "lock" in prov:
        return {"locked_at_display": lock["locked_at_display"], "sha256": lock["sha256"],
                "sha256_prefix": "sha256 " + lock["sha256"][:12]}[prov["lock"]]
    raise AssertionError(f"unknown provenance {prov}")


class RenderTests(unittest.TestCase):
    def setUp(self):
        self.ws = Workspace()
        self.ds = self.ws.ingest()
        self.cfg = config()
        self.results = model.compute(self.cfg, self.ds)
        self.lock = self.ws.lock()[0]

    def tearDown(self):
        self.ws.cleanup()

    def test_template_has_no_digits(self):
        with open(TEMPLATE, encoding="utf-8") as fh:
            text = fh.read().replace('charset="utf-8"', "")
        self.assertIsNone(re.search(r"\d", text), "a digit was typed into the report template")

    def test_rendered_numbers_trace(self):
        page, entries = build_html(self.cfg, self.ds, self.results, self.lock)
        for e in entries:
            self.assertEqual(e["text"], resolve(e, self.ds, self.results, self.cfg, self.lock), e)
        texts = [e["text"] for e in entries]
        for tok in NUM_TOKEN.findall(body_text(page)):
            self.assertTrue(any(tok in t for t in texts), f"number {tok!r} on the page traces to no dataset/results value")
        self.assertIn("$420M", texts)  # the claim's own math is on page one

    def test_partial_render_marks_insufficient(self):
        # fixtures carry no launch-day rows: twitch_peak_nov19 / ttwo_close_nov19 are absent
        page, _ = build_html(self.cfg, self.ds, self.results, self.lock)
        for rid in ("twitch_peak_nov19", "ttwo_close_nov19"):
            self.assertRegex(page, rf"insufficient data — missing: [^<]*{rid}")
        with self.assertRaises(MissingInputError):
            render(self.cfg, self.ds, self.results, self.lock, os.path.join(self.ws.dir, "out"), allow_partial=False)

    def test_core_missing_refuses_render_even_with_allow_partial(self):
        ds = {k: v for k, v in self.ds.items() if k != "claim_workers"}
        results = model.compute(self.cfg, ds)
        with self.assertRaises(MissingInputError):
            render(self.cfg, ds, results, self.lock, os.path.join(self.ws.dir, "out"), allow_partial=True)

    def test_proxy_labels_survive(self):
        page, _ = build_html(self.cfg, self.ds, self.results, self.lock)
        label = html.escape(self.ds["trends_doordash_nov12"]["label"])
        self.assertRegex(page, re.escape(label) + r' <span class="tag proxy">proxy</span>')

    def test_precedent_section_omitted_without_source(self):
        page, _ = build_html(self.cfg, self.ds, self.results, self.lock)
        self.assertNotIn("no dent was reported", page.lower())

    def test_render_smoke(self):
        chrome = find_chrome()
        if not chrome:
            self.skipTest("Chromium not found — PDF/PNG smoke test SKIPPED")
        out = render(self.cfg, self.ds, self.results, self.lock, os.path.join(self.ws.dir, "out"), allow_partial=True)
        self.assertEqual(pdf_page_count(out["pdf"]), 3)
        self.assertEqual(len(out["pngs"]), 3)
        for png in out["pngs"]:
            with open(png, "rb") as fh:
                head = fh.read(24)
            self.assertEqual(head[:8], b"\x89PNG\r\n\x1a\n")
            w, h = struct.unpack(">II", head[16:24])
            self.assertEqual((w, h), (1080, 1350), png)
        self.assertTrue(os.path.isfile(out["fact_sheet"]))


if __name__ == "__main__":
    unittest.main()

"""Render the 3-page report: HTML from string.Template, then headless Chromium -> PDF + page PNGs.

Every number reaches the page through Tracer.num()/Tracer.text(), which records where it came
from (dataset id, results path, or lock field). fact-sheet.json is that record: the only numbers
the caption/methodology writer may quote. Templates contain no digits (a test enforces it).
"""
import glob
import html
import json
import os
import re
import shutil
import string
import subprocess

from .errors import MissingInputError, PipelineError
from .model import core_missing

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATES = os.path.join(os.path.dirname(HERE), "templates")
PAGE_W, PAGE_H = 1080, 1350


# ---- number formatting --------------------------------------------------------------------

def _sig(x):
    """Three significant figures, never scientific notation (callers keep |x| < 1e5)."""
    s = f"{x:.3g}"
    return f"{x:.0f}" if "e" in s else s


def _compact(v):
    a = abs(v)
    for div, suf in ((1e12, "T"), (1e9, "B"), (1e6, "M")):
        if a >= div:
            return _sig(v / div) + suf
    if a >= 1e5:
        return _sig(v / 1e3) + "K"
    if a >= 1000:
        return f"{v:,.0f}"
    return _sig(v)


def fmt(value, unit):
    if value is None:
        raise MissingInputError("fmt() called with a missing value")
    if unit == "pct":
        p = value * 100
        return (f"{p:.1f}".rstrip("0").rstrip(".")) + "%"
    if unit in ("usd", "usd_per_day"):
        sign = "-" if value < 0 else ""
        return sign + "$" + _compact(abs(value))
    if unit == "usd_per_share":
        return f"${value:,.2f}"
    if unit == "count":
        return _compact(value)
    return f"{value:g}"


class Tracer:
    def __init__(self):
        self.entries = []

    def num(self, value, unit, prov):
        s = fmt(value, unit)
        self.entries.append({"text": s, "value": value, "unit": unit, "provenance": prov})
        return html.escape(s)

    def text(self, s, prov):
        self.entries.append({"text": s, "provenance": prov})
        return html.escape(s)


# ---- context ------------------------------------------------------------------------------

def _get(results, path):
    node = results
    for p in path.split("."):
        node = node[p]
    return node


class Builder:
    def __init__(self, config, dataset, results, lock):
        self.c, self.d, self.r, self.lock = config, dataset, results, lock
        self.t = Tracer()

    # dataset values
    def dnum(self, rid):
        f = self.d[rid]
        return self.t.num(f["value"], f["unit"], {"dataset": rid, "field": "value"})

    def dtext(self, rid, field):
        return self.t.text(self.d[rid][field], {"dataset": rid, "field": field})

    def label(self, rid):
        lab = self.dtext(rid, "label")
        if self.d[rid]["kind"] == "proxy":
            lab += ' <span class="tag proxy">proxy</span>'
        return lab

    # results values
    def rnum(self, path, unit):
        return self.t.num(_get(self.r, path), unit, {"results": path})

    def insufficient(self, path):
        ids = _get(self.r, path).get("missing", [])
        idtxt = ", ".join(self.t.text(i, {"results": path + ".missing", "id": i}) for i in ids)
        return f'<span class="insufficient">insufficient data — missing: {idtxt}</span>'

    def ok(self, path):
        return _get(self.r, path).get("status") == "complete"

    def source_line(self, rid):
        f = self.d[rid]
        return (f'{self.dtext(rid, "source_name")} '
                f'<span class="dim">({self.dtext(rid, "as_of")} · {html.escape(f["kind"])})</span>')

    # ---- sections ----
    def claim_block(self):
        p = "claim_audit"
        if not self.ok(p):
            return self.insufficient(p)
        ids = self.c[p]["inputs"]
        return (f'<div class="claim-row">'
                f'<div class="claim-cell"><div class="k">The viral claim</div><div class="big strike">{self.rnum(p + ".headline_usd", "usd")}</div></div>'
                f'<div class="claim-cell"><div class="k">Its own inputs produce</div><div class="big">{self.rnum(p + ".reproduced_usd", "usd")}</div>'
                f'<div class="sub">{self.dnum(ids["workers"])} workers × {self.dnum(ids["output_per_day"])} per day</div></div>'
                f'</div>')

    def range_block(self):
        need = ["costs.low_base", "costs.high_base"]
        if not all(self.ok(p) for p in need):
            bad = [p for p in need if not self.ok(p)]
            return "".join(self.insufficient(p) for p in bad)
        out = (f'<div class="k">This report’s productivity range (base output rate)</div>'
               f'<div class="big accent">{self.rnum("costs.low_base.usd", "usd")} – {self.rnum("costs.high_base.usd", "usd")}</div>'
               f'<div class="sub">{self.rnum("absence_cases.low.absences", "count")} to '
               f'{self.rnum("absence_cases.high.absences", "count")} absences × '
               f'{self.rnum("output_per_worker_day.base.usd_per_day", "usd_per_day")} output per worker-day</div>')
        if self.ok("costs.low_sensitivity") and self.ok("costs.high_sensitivity"):
            out += (f'<div class="sub">Sensitivity at GDP per employed person '
                    f'({self.rnum("output_per_worker_day.sensitivity.usd_per_day", "usd_per_day")}/day): '
                    f'{self.rnum("costs.low_sensitivity.usd", "usd")} – {self.rnum("costs.high_sensitivity.usd", "usd")}</div>')
        else:
            out += f'<div class="sub">Sensitivity case: {self.insufficient("output_per_worker_day.sensitivity")}</div>'
        return out

    def superbowl_block(self):
        p = "benchmarks.superbowl"
        node = _get(self.r, p)
        if node["status"] != "complete":
            return self.insufficient(p)
        rid = self.c["benchmarks"]["superbowl"]["inputs"]["absences"]
        return (f'<div class="k">Yardstick: {self.dtext(rid, "label")}</div>'
                f'<div class="mid">{self.rnum(p + ".absences", "count")} absences '
                f'<span class="dim">≈ {self.rnum(p + ".dollar_equivalent_usd", "usd")} at the base output rate</span></div>'
                f'<div class="src">{self.source_line(rid)}</div>')

    def anchors_block(self):
        cells = []
        for rid in self.c["anchors"]["optional"]:
            if rid in self.r["anchors"]["present"]:
                cells.append(f'<div class="anchor"><div class="mid">{self.dnum(rid)}</div>'
                             f'<div class="k">{self.label(rid)}</div><div class="src">{self.source_line(rid)}</div></div>')
            else:
                idt = self.t.text(rid, {"results": "anchors.missing", "id": rid})
                cells.append(f'<div class="anchor"><span class="insufficient">insufficient data — missing: {idt}</span></div>')
        return '<div class="anchors">' + "".join(cells) + "</div>"

    def precedent_block(self):
        node = self.r["benchmarks"]["precedent_gtav_2013"]
        if not node["rendered"]:
            return ""  # decision 8: omitted entirely without a sourced row
        rid = node["row"]
        return (f'<div class="block"><div class="k">Precedent, not a measurement: {self.dtext(rid, "label")}</div>'
                f'<div class="mid">{self.dnum(rid)}</div>'
                f'<p>{html.escape(node["wording"]).capitalize()}.</p><div class="src">{self.source_line(rid)}</div></div>')

    def inputs_table(self):
        ids = []
        for sec in (self.c["claim_audit"], self.c["output_per_worker_day"]["base"],
                    self.c["output_per_worker_day"]["sensitivity"], self.c["absence_cases"]["low"],
                    self.c["absence_cases"]["high"], self.c["benchmarks"]["superbowl"]):
            ids += [i for i in sec["inputs"].values() if i not in ids]
        rows = []
        for rid in ids:
            if rid in self.d and self.d[rid].get("value") is not None:
                rows.append(f'<tr><td>{self.label(rid)}</td><td class="num">{self.dnum(rid)}</td>'
                            f'<td>{html.escape(self.d[rid]["kind"])}</td><td>{self.source_line(rid)}</td></tr>')
            else:
                idt = self.t.text(rid, {"missing_input": rid})
                rows.append(f'<tr><td colspan="4"><span class="insufficient">insufficient data — missing: {idt}</span></td></tr>')
        return ('<table class="inputs"><thead><tr><th>Input</th><th>Value</th><th>Kind</th><th>Source</th></tr></thead>'
                f'<tbody>{"".join(rows)}</tbody></table>')

    def grid(self):
        head = '<tr><th></th><th>Absences</th><th>× base rate</th><th>× sensitivity rate</th></tr>'
        rows = []
        for case in self.c["costs"]["cases"]:
            a = f"absence_cases.{case}"
            ab = self.rnum(a + ".absences", "count") if self.ok(a) else self.insufficient(a)
            cells = []
            for rate in self.c["costs"]["rates"]:
                p = f"costs.{case}_{rate}"
                cells.append(f'<td class="num">{self.rnum(p + ".usd", "usd") if self.ok(p) else self.insufficient(p)}</td>')
            rows.append(f'<tr><th>{html.escape(case.capitalize())} case</th><td class="num">{ab}</td>{"".join(cells)}</tr>')
        return f'<table class="grid"><thead>{head}</thead><tbody>{"".join(rows)}</tbody></table>'

    def context_block(self):
        items = []
        for rid in self.c["context"]["survey_intent"]:
            if rid in self.r["context"]["present"]:
                items.append(f'<li>{self.label(rid)}: <b>{self.dnum(rid)}</b> — {self.source_line(rid)}</li>')
        for rid in self.c["proxies"]["optional"]:
            if rid in self.r["proxies"]["present"]:
                items.append(f'<li>{self.label(rid)}: <b>{self.dnum(rid)}</b> — {self.source_line(rid)}</li>')
        if not items:
            return ""
        note = html.escape(self.c["context"]["survey_intent_note"])
        return f'<div class="block"><div class="k">Context ({note})</div><ul>{"".join(items)}</ul></div>'

    def formulas(self):
        c = self.c
        lines = [("Claim reproduction", c["claim_audit"]["formula"]),
                 ("Output per worker-day, base", c["output_per_worker_day"]["base"]["formula"]),
                 ("Output per worker-day, sensitivity", c["output_per_worker_day"]["sensitivity"]["formula"]),
                 ("Absences, low case", c["absence_cases"]["low"]["formula"]),
                 ("Absences, high case", c["absence_cases"]["high"]["formula"]),
                 ("Cost", c["costs"]["formula"])]
        lis = "".join(f'<li><b>{html.escape(k)}:</b> <code>{html.escape(v)}</code></li>' for k, v in lines)
        conv = []
        for name, entry in c["conventions"].items():
            unit = "count"
            conv.append(f'<li><code>{html.escape(name)}</code> = '
                        f'{self.t.num(entry["value"], unit, {"config": "conventions." + name})} '
                        f'<span class="dim">({html.escape(entry["label"])})</span></li>')
        bases = (f'<li><b>Low case basis:</b> {html.escape(c["absence_cases"]["low"]["basis"])}</li>'
                 f'<li><b>High case basis:</b> {html.escape(c["absence_cases"]["high"]["basis"])}</li>'
                 f'<li><b>Base output rate:</b> {html.escape(c["output_per_worker_day"]["base"]["basis"])}</li>')
        return f'<ul class="formulas">{lis}{bases}</ul><div class="k">Conventions</div><ul>{"".join(conv)}</ul>'

    def lock_line(self):
        return (f'Method locked {self.t.text(self.lock["locked_at_display"], {"lock": "locked_at_display"})} · '
                f'{self.t.text("sha256 " + self.lock["sha256"][:12], {"lock": "sha256_prefix"})}')

    def sources_small(self):
        seen, parts = set(), []
        for rid in sorted(self.d):
            name = self.d[rid]["source_name"]
            if name not in seen:
                seen.add(name)
                parts.append(self.dtext(rid, "source_name"))
        return " · ".join(parts)

    def context(self):
        with open(os.path.join(TEMPLATES, "report.css"), encoding="utf-8") as fh:
            css = fh.read()
        return {
            "css": css,
            "claim_block": self.claim_block(),
            "range_block": self.range_block(),
            "superbowl_block": self.superbowl_block(),
            "anchors_block": self.anchors_block(),
            "inputs_table": self.inputs_table(),
            "grid": self.grid(),
            "context_block": self.context_block(),
            "precedent_block": self.precedent_block(),
            "formulas": self.formulas(),
            "lock_line": self.lock_line(),
            "lock_hash_full": self.t.text(self.lock["sha256"], {"lock": "sha256"}),
            "sources_small": self.sources_small(),
        }


def build_html(config, dataset, results, lock):
    b = Builder(config, dataset, results, lock)
    with open(os.path.join(TEMPLATES, "report.html.tmpl"), encoding="utf-8") as fh:
        tmpl = string.Template(fh.read())
    page = tmpl.substitute(b.context())  # KeyError on any unfilled $placeholder: fails loudly
    return page, b.t.entries


# ---- chromium -----------------------------------------------------------------------------

def find_chrome():
    env = os.environ.get("GTA_CHROME")
    if env and os.path.isfile(env):
        return env
    hits = sorted(glob.glob(os.path.expanduser("~/.cache/ms-playwright/chromium-*/chrome-linux64/chrome")))
    if hits:
        return hits[-1]
    for name in ("chromium", "chromium-browser", "google-chrome"):
        p = shutil.which(name)
        if p:
            return p
    return None


def _chrome(chrome, args, url):
    cmd = [chrome, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
           "--no-first-run", "--disable-dev-shm-usage", *args, url]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if proc.returncode != 0:
        raise PipelineError(f"chromium failed ({proc.returncode}): {proc.stderr[-800:]}")


def split_pages(page_html):
    """One standalone HTML per <section class="page">, for per-page PNG screenshots."""
    head, rest = page_html.split("<body>", 1)
    sections = re.findall(r'<section class="page[^"]*">.*?</section>', rest, re.S)
    return [f"{head}<body class=\"single\">{s}</body></html>" for s in sections]


def pdf_page_count(path):
    with open(path, "rb") as fh:
        data = fh.read()
    return len(re.findall(rb"/Type\s*/Page(?![s\w])", data))


def render(config, dataset, results, lock, out_dir, allow_partial=False, chrome=None, basename="gta-vi-launch-impact"):
    missing = core_missing(config, results)
    if missing:
        raise MissingInputError(f"core sections incomplete, render refused (even with --allow-partial): {missing}")
    incomplete_optional = [i for g in ("anchors",) for i in results[g]["missing"]]
    if incomplete_optional and not allow_partial:
        raise MissingInputError(f"optional anchors missing {incomplete_optional}; pass --allow-partial to render "
                                "them as 'insufficient data'")
    os.makedirs(out_dir, exist_ok=True)
    page_html, entries = build_html(config, dataset, results, lock)
    html_path = os.path.join(out_dir, basename + ".html")
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(page_html)
    with open(os.path.join(out_dir, "fact-sheet.json"), "w", encoding="utf-8") as fh:
        json.dump({"lock": lock, "figures": entries}, fh, indent=2)
    out = {"html": html_path, "fact_sheet": os.path.join(out_dir, "fact-sheet.json"), "pdf": None, "pngs": []}
    chrome = chrome or find_chrome()
    if not chrome:
        raise PipelineError("Chromium not found: set GTA_CHROME or install the Playwright Chromium build")
    pdf = os.path.join(out_dir, basename + ".pdf")
    _chrome(chrome, ["--no-pdf-header-footer", f"--print-to-pdf={pdf}"], "file://" + os.path.abspath(html_path))
    out["pdf"] = pdf
    tmp_dir = os.path.join(out_dir, "_pages")
    os.makedirs(tmp_dir, exist_ok=True)
    try:
        for n, single in enumerate(split_pages(page_html), 1):
            ph = os.path.join(tmp_dir, f"page-{n}.html")
            with open(ph, "w", encoding="utf-8") as fh:
                fh.write(single)
            png = os.path.join(out_dir, f"page-{n}.png")
            _chrome(chrome, [f"--window-size={PAGE_W},{PAGE_H}", f"--screenshot={png}"], "file://" + ph)
            out["pngs"].append(png)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
    return out

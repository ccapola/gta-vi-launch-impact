# GTA VI Launch-Impact Pipeline — Build Plan

*Plan-only pass by Claude Code (session "gta-vi-pipeline"), Wed Nov 18, 2026. Nothing was built. Execution waits for Cooper's approval.*

## Environment (checked, not assumed)

- Python 3.12.3 and matplotlib are on the VM. jinja2, pytest, and pypdf are NOT — the plan uses the standard library only, plus the headless Chromium already installed (Playwright build), so nothing new gets installed.
- `hidden_files/data/` doesn't exist yet; today's 12:30 PM baseline pull creates it.
- Timing note from Claude Code: the method must be locked before the Nov 19 launch, so approval is needed today.

## What gets built

```
pipeline/
  run.py                  # CLI: ingest | freeze | verify-freeze | compute | render | all
  config/
    model_frozen.json     # the locked method (below)
    model_frozen.lock     # SHA-256 of config + model.py, lock time (ET), Python version
  gta_audit/
    __init__.py
    errors.py             # MissingInputError, EvidenceError, FreezeError
    parse.py              # turns "9.69M", "$942M", "+13%", "1,530" into numbers; refuses anything unclear
    dataset.py            # loads and checks figures.csv, writes data/dataset.json
    ingest.py             # confirms each figure's quote appears word-for-word in its source markdown file
    freeze.py             # writes and checks the lock hash
    model.py              # the formulas; no numeric defaults anywhere
    render.py             # HTML from templates, then headless Chromium makes the PDF and PNGs
  templates/
    report.html.tmpl      # 3 pages; stdlib string.Template, $placeholders only
    report.css
  data/
    figures.csv           # figures transcribed from hidden_files/data/*.md (input)
    dataset.json          # checked dataset (generated)
    results.json          # model output (generated)
  tests/
    fixtures/             # small sample markdown + figures, used only by tests
    test_*.py             # unittest (section: Tests)
files/report/             # build output
  gta-vi-launch-impact.html
  gta-vi-launch-impact.pdf        # LinkedIn document post, 3 pages
  page-1.png, page-2.png, page-3.png
  fact-sheet.json                 # the only numbers the caption/methodology writer may quote
```

**How the markdown gets in:** the pull agents write free-form markdown, and parsing that automatically would break easily. Instead, each figure is copied by hand into `figures.csv` together with a word-for-word quote from the markdown. `ingest.py` then refuses any row whose quote isn't actually in the cited file. That check is what stops numbers from being made up. (If a pull writes a structured figures block, ingest can read it directly — see open question 6.)

## Dataset schema (figures.csv — one row per figure)

| field | type | rule |
|---|---|---|
| id | slug | unique, e.g. `bamboohr_pto_delta_nov19` |
| label | text | how the figure is named in the report |
| value | number | must parse cleanly; no ranges in one cell (split into `_low` / `_high` rows) |
| unit | enum | usd, usd_per_day, count, pct, ratio, index, usd_per_share |
| kind | enum | measured, survey, estimate, proxy, claim, benchmark, precedent |
| snapshot | enum | baseline (Nov 18), launchday (Nov 20), reference (stable facts such as BLS employment) |
| as_of | date | date of the figure, not the date it was pulled |
| source_name | text | required, e.g. "BambooHR platform data" |
| source_url | url | required unless the source is "survey press release, no URL" (must be stated) |
| evidence_file | path | the hidden_files/data/*.md file it came from |
| evidence_quote | text | must appear word for word in evidence_file (whitespace ignored) |
| notes | text | optional |

Checks on load: every required field filled; ids unique; the quote is found in the cited file; any row marked `proxy` keeps a "proxy" label wherever it's rendered. All problems are listed in one go. There are no default values anywhere.

## Model config (model_frozen.json), locked today

Every number in the config points at a dataset id. The only values written into the config itself are labeled conventions.

- **conventions:** working_days_per_year = 250 ("assumption: standard full-time year")
- **claim_audit:** claim_workers × claim_output_per_day, with expected_reproduction_usd = 420,000,000 — the professor's own inputs (1.5M × ~$280) must reproduce ~$420M, or the build fails.
- **output_per_worker_day:** base = avg annual output per worker / 250 (~$70K / 250 = ~$280, matching the claim's own inputs); sensitivity = US GDP / US employed / 250.
- **absence_cases:**
  - low = us_employed × baseline_daily_absence_rate × bamboohr_pto_delta_nov19 — basis: measured PTO increase above a normal Thursday (BambooHR platform)
  - high = ft_employed_gamers × gamesquare_skip_rate — basis: survey intent (overstates by nature)
- **outputs:** cost[case][output_rate] = absences[case] × output_per_day[rate]
- **sanity cap:** high-case absences must be below Super Bowl Monday 2025 absences, or the build stops with an explanation.
- **benchmarks:** Super Bowl Monday (absences; dollar equivalent shown at base rate — open question 7); GTA V 2013 (day-1 revenue + BLS absence note; framing: precedent, not a measurement).
- **required_for_render:** page-1 core = claim_audit, absence_cases, output_per_worker_day.base, benchmarks. Page-1 anchors optional = preorders_units, preorders_usd, twitch_peak_nov19, ttwo_close_nov19.

**The lock:** `run.py freeze` records the SHA-256 of model_frozen.json and model.py together, with the time in ET. `verify-freeze` checks that hash before every compute and render and stops the build if either file changed. The report footer prints: "Method locked Nov 18, 2026 [time] ET · sha256 [first 12 chars]".

## Render approach

- Templates use Python's built-in string.Template; every $placeholder is filled from results/dataset. The templates contain no digits except in CSS, and a test enforces that — so no number can be hand-typed into the report.
- Pages are 1080×1350 (4:5, the LinkedIn document-post size), one HTML file, three pages:
  - **Page 1 — Report visual:** the claim and the audit ($1B claim, $420M its own math, this report's productivity range), then the hard anchors, the "what we can't measure" line, sources in small print.
  - **Page 2 — Model table:** each input with its value, source, and kind; the case grid.
  - **Page 3 — Methodology:** the formulas as written, the lock hash and time, the limits.
- Output: the VM's Chromium runs `--headless=new --print-to-pdf` plus page PNGs.
- Missing data: a section with missing inputs renders as a visible "insufficient data" mark — never a silent blank and never a filled-in guess.

## Tests (unittest)

1. **test_claim_reproduction_420m (required):** 1.5M workers × $280/day = $420M through the real model path.
2. test_no_numeric_defaults: scans the model function signatures and finds no numeric defaults.
3. test_parse_units: "9.69M", "$942M", "+13%", "1,530" parse correctly.
4. test_ingest_rejects_missing_quote: a figure whose quote isn't in its evidence file fails ingest.
5. test_freeze_tamper_detection: editing the config or model after the freeze makes verify-freeze fail.
6. test_rendered_numbers_trace: every number in the rendered HTML matches a dataset/results value.
7. test_partial_render_marks_insufficient: when launch-day data is missing, the render marks it instead of inventing it.
8. test_proxy_labels_survive: proxy figures render with their proxy label.
9. test_render_smoke: the PDF has 3 pages (counted from page objects) and the PNGs exist; skips cleanly if Chromium is missing, and the skip is reported.
10. test_high_below_superbowl_cap: the sanity cap holds, or the build stops with an explanation.

## Run order

**Today, Nov 18 — after approval, before launch:**
1. Build the pipeline and tests; run the suite.
2. After the 12:30 PM baseline pull lands, transcribe the baseline figures into figures.csv with their quotes; run ingest.
3. Run `run.py freeze` — the method is locked today, before the game exists.

**Fri, Nov 20 — after the 9:30 AM pull:**
1. Transcribe the launch-day figures into figures.csv with their quotes; run ingest.
2. Run verify-freeze.
3. Run `compute --dry`: reports which sections are complete or incomplete. No render yet.

**Mon, Nov 23, 10:00 AM build:**
1. Run verify-freeze. If it fails, the build stops.
2. Run the full test suite. If any test fails, the build stops.
3. Run ingest, then compute, then `render --allow-partial` (partial allowed only for non-core sections).
4. Check the PNGs and PDF visually.
5. The methodology note and caption are written from fact-sheet.json only.
6. Deliver to Cooper as the scheduled build describes.

## Open questions for Cooper (from Claude Code)

1. **The low-case formula needs a fix.** BambooHR's +13% is an increase in PTO requests, not an absence rate — the plan adds a sourced "normal daily absence rate" figure and applies the +13% lift to it. (Muse's recommendation: accept the fix.)
2. **The high case needs a defined population.** Two candidates: BambooHR's 18% of salaried workers who *planned* to take the day (broad, intent-based) vs GameSquare's 10% of full-time-working gamers (narrower, defined population). The plan's config uses the GameSquare version. (Recommendation: keep GameSquare as the high case; cite the 18% as survey-intent context.)
3. **The professor's claim needs a citation.** Who he is and where his 1.5M / $280 inputs were published must be a sourced dataset row, not folklore. (Known so far: José García-Montalvo, Pompeu Fabra University, via press coverage — today's baseline pull is tasked with capturing a citable source.)
4. **The output figure is arguably low.** $70K/year is closer to a wage than to output per worker; GDP per employed person is far higher (~$190K+, ≈$760/day). The plan keeps $280 as the base (it matches the claim's own inputs, so the audit is apples-to-apples) and shows the GDP figure as the sensitivity case. (Recommendation: keep it that way — it's the more defensible audit.)
5. **Proof of the pre-launch lock.** A hash on this machine is only our own record. Stronger: commit the frozen config to Cooper's GitHub today, giving it a public timestamp. (Recommendation: do the GitHub commit.)
6. **Change the scheduled pulls slightly.** Claude Code would like the Nov 20 pull to also write a structured figures block, so ingest can read it directly instead of relying on hand transcription. (Recommendation: yes — small change to that one job.)
7. **Super Bowl comparison:** absences only, or also the dollar equivalent at the base rate? (Recommendation: both — it's the comparison readers will make anyway.)
8. **GTA V 2013 precedent needs a citation too.** The "no measurable dent" line must trace to a source (BLS absence data / contemporary coverage); if none is found, the report softens it to what the source actually supports. (Recommendation: accept the fallback.)

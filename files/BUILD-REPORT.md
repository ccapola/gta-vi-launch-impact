# Build Report — GTA VI Launch-Impact Pipeline

*Execution of files/BUILD-BRIEF.md against the approved files/PIPELINE-PLAN.md. Claude Code, Wed Nov 18, 2026.*

## Status at a glance

| Item | Result |
|---|---|
| Pipeline build | Done. Standard library only, nothing installed |
| Test suite | **24 / 24 passed, 0 skipped.** The required `test_claim_reproduction_420m` passes |
| Baseline transcription | 20 figures transcribed, and ingest passes (every quote matched word for word) |
| Method freeze | **LOCKED: Nov 18, 2026 12:38 PM ET · sha256 `535ead6ba13c`** (full: `535ead6ba13c2195bc2b7cf6911dceadaf636a2a507e5fe60081947a322afa47`). verify-freeze passes |
| Git | Local commit `1fff200` (frozen config + model + lock). **Not pushed: no remote exists.** Pushing to GitHub needs Cooper's repo |
| Real-data render | Not run, as the brief requires. Only fixtures were rendered |
| **Data gaps (blocks the Nov 23 render)** | **None of the core sections are complete yet.** The baseline pull didn't capture the claim inputs, the absence rate, US employed, full-time-employed gamers, output per worker, or Super Bowl absences. Details are below |

## What was built

```
pipeline/
  run.py                    ingest | freeze | verify-freeze | compute [--dry] | render [--allow-partial] [--out] | all
  config/model_frozen.json  the locked method (all inputs are dataset ids; the only numbers are labeled conventions + the $420M check)
  config/model_frozen.lock  sha256 over config + model.py, lock time in ET, Python version
  gta_audit/errors.py       ParseError, MissingInputError, EvidenceError, FreezeError, SanityError
  gta_audit/parse.py        "9.69M" "$942M" "+13%" "1,530" → numbers; refuses ~, <, ranges, words, bad commas
  gta_audit/dataset.py      schema checks, all problems reported at once, no defaults
  gta_audit/ingest.py       word-for-word evidence check; reads figures.csv and ```figures blocks
  gta_audit/freeze.py       lock / verify; refuses to re-lock an existing lock
  gta_audit/model.py        formulas, no numeric defaults; sanity checks raise
  gta_audit/render.py       string.Template → HTML; headless Chromium → 3-page PDF + page PNGs; fact-sheet.json
  templates/report.html.tmpl, report.css   template has no digits (test-enforced)
  data/figures.csv          baseline transcription (20 rows)
  data/dataset.json         checked dataset (generated)
  tests/                    unittest; fixtures/ = TEST FIXTURE evidence + figures only
```

How the eight decisions landed in the build:
1. **Low case** = `us_employed × baseline_daily_absence_rate × bamboohr_pto_lift_nov19`. The +13% is used only as a lift. A test checks the formula as 160M × 3% × 13%.
2. **High case** = `ft_employed_gamers × gamesquare_skip_rate`. BambooHR's 18% appears only in `context.survey_intent`, and the report labels it "survey-intent context only; never a model case."
3. **Professor citation:** see Deviations. The baseline file has no García-Montalvo source at all.
4. **Output per worker-day:** base = `avg_annual_output_per_worker / 250`. GDP per employed person (`us_gdp_usd / us_employed / 250`) is the sensitivity case only.
5. **Lock proof:** local git commit made. No push (no remote).
6. **Structured figures block:** implemented and tested (format below).
7. **Super Bowl:** the section shows absences and the dollar equivalent at the base rate. It counts as complete only when both exist. The sanity cap (high case below Super Bowl) stops the build if it fails.
8. **GTA V 2013 precedent:** **landed as OMITTED.** The baseline has no sourced row. The section renders "no dent was reported in contemporary coverage" only when a row `gtav_2013_precedent` with `kind=precedent` exists. Tests confirm it is absent from the page otherwise.

## Test results (`python3 -m unittest discover -s pipeline/tests`): 24 ran, 24 OK, 0 skipped

All 10 plan tests are present and pass:
1. `test_claim_reproduction_420m` (required) runs 1.5M × $280 = $420M through the real ingest → frozen config → model path. **PASS**
2. `test_no_numeric_defaults` PASS
3. `test_parse_units` PASS
4. `test_ingest_rejects_missing_quote` PASS
5. `test_freeze_tamper_detection` (config edit and model edit each break verify) PASS
6. `test_rendered_numbers_trace`: every number on the page re-derives from its recorded dataset/results/lock/config source. PASS
7. `test_partial_render_marks_insufficient`: missing launch-day anchors render as "insufficient data — missing: …", and render without `--allow-partial` refuses. PASS
8. `test_proxy_labels_survive` PASS
9. `test_render_smoke`: Chromium found, the PDF has 3 page objects, and 3 PNGs come out at 1080×1350. PASS (not skipped)
10. `test_high_below_superbowl_cap`: the cap holds, and breaking it raises SanityError with an explanation. PASS

Additional tests: `test_claim_reproduction_mismatch_stops`, `test_low_case_is_lift_on_absence_rate`, `test_missing_core_input_fails_loudly`, `test_precedent_omitted_without_source_row`, `test_parse_refuses_unclear`, `test_ingest_ok`, `test_ingest_rejects_empty_required_field_and_duplicates`, `test_figures_block_read_directly`, `test_figures_block_cannot_vouch_for_itself`, `test_freeze_refuses_relock`, `test_verify_without_lock_fails`, `test_core_missing_refuses_render_even_with_allow_partial`, `test_precedent_section_omitted_without_source`, `test_template_has_no_digits`.

I also checked the fixture render by eye in a scratch folder: three clean 4:5 pages, the insufficient-data marks are visible, and the proxy tag shows. Nothing was written to `files/report/`.

## Freeze and lock details

- Baseline file `hidden_files/data/baseline-2026-11-18.md` was already there when I reached this step (written 12:29 PM), so I didn't need to wait.
- Order: tests passed → 20 figures transcribed → `run.py ingest` OK → `run.py freeze` → `run.py verify-freeze` OK.
- **Lock time: Nov 18, 2026 12:38 PM ET (2026-11-18T12:38:30-05:00). sha256 prefix `535ead6ba13c`.**
- The freeze locks the **method** (config + formulas), not the data. Inputs that arrive later are matched to the frozen dataset ids. Any change to `model_frozen.json` or `model.py` now stops every compute and render.
- `freeze` refuses to overwrite an existing lock. Re-locking after launch would void the "method written before launch" claim, so it requires deleting the lock by hand on Cooper's decision.

## Baseline transcription (data/figures.csv)

These 20 rows come from the baseline file, each with a word-for-word quote:
- **BambooHR:** PTO lift Nov 19 (13%) and Nov 20 (11%); platform base 3.4M; survey 18% salaried and 32% Gen Z (context only); n = 1,530
- **GameSquare:** 10% skip rate (the high-case rate); 30% considering; n = 1,000
- **Sensor Tower preorders:** Nov 17 reading of 15.88M / $1.54B (the page-1 anchor) and Nov 10 reading of 9.69M / $942M (kept with its date)
- **Kalshi:** album streams forecast of 93M
- **TTWO:** Nov 17 close $203.93; Nov 18 intraday $218.20
- **Logitech:** 7,000 employees given a gaming day off
- **Google Trends:** DoorDash index on the Oct 29 / Nov 5 / Nov 12 Thursdays (5 / 4 / 3), tagged proxy

I left out the sick-term Trends values because they are "<1", and the parser correctly refuses a value that is only an inequality.

**Gaps still open.** None of these are in the baseline file, and every core section is incomplete until they are sourced:

| Section | Missing dataset ids |
|---|---|
| claim_audit | `claim_headline_usd`, `claim_workers`, `claim_output_per_day` |
| absence_cases | `baseline_daily_absence_rate`, `us_employed`, `ft_employed_gamers` |
| output_per_worker_day.base | `avg_annual_output_per_worker` (sensitivity also needs `us_gdp_usd`) |
| benchmarks.superbowl | `superbowl_monday_absences_2025` |
| anchors (launch day, expected Nov 20) | `twitch_peak_nov19`, `ttwo_close_nov19` (+ proxy `trends_doordash_nov19`) |

These are reference statistics (BLS, BEA, UKG) and the professor's press coverage, so they don't depend on launch. They still need a captured source file with quotes before the Nov 23 build. Without them, `render` refuses to run, even with `--allow-partial`.

## Structured figures block (decision 6). This is the format Muse should have the Nov 20 pull emit

Put it in the pull's markdown file, e.g. `hidden_files/data/launchday-2026-11-20.md`. `run.py ingest` reads every `*.md` in `hidden_files/data/` automatically:

````
```figures
id,label,value,unit,kind,snapshot,as_of,source_name,source_url,evidence_quote,notes
twitch_peak_nov19,GTA VI peak Twitch viewers (Nov 19),6.2M,count,measured,launchday,2026-11-19,TwitchTracker,https://twitchtracker.com/...,"peaked at 6.2M concurrent viewers",
```
````

Rules:
- The columns are the figures.csv header minus `evidence_file`, which is set to the file the block sits in. Standard CSV quoting applies.
- `value` must be one clean number: `6.2M`, `$1.54B`, `13%`, `$218.20`, `1,530`. Anything with `~`, `<`, ranges or words is refused. Put "approximately" wording in `notes`.
- `unit` must be one of usd, usd_per_day, count, pct, ratio, index, usd_per_share. `kind` must be one of measured, survey, estimate, proxy, claim, benchmark, precedent. `snapshot` must be one of baseline, launchday, reference. `as_of` uses YYYY-MM-DD.
- `source_url` is a URL, or `no URL: <reason>`.
- `evidence_quote` must appear word for word (whitespace-insensitive) in the same file **outside** the figures block, so a block can never vouch for itself.
- An id defined in both the CSV and a block, or in two blocks, is an error. Nothing is silently overridden.
- Use the frozen ids the config expects for Nov 20: `twitch_peak_nov19`, `ttwo_close_nov19`, `trends_doordash_nov19`.

The fallback (hand transcription into `pipeline/data/figures.csv` with quotes) still works unchanged.

## Git / push outcome

- I ran `git init` in the project folder (there was no repo). The commit is `1fff2001cd1c`, "Pre-launch method freeze: GTA VI launch-impact model", committed 12:38:39 PM ET. Author: `Muse (Cooper's agent)` (the global git identity). It contains only `model_frozen.json`, `model_frozen.lock` and `model.py`.
- **Push: not attempted.** No remote named origin exists. To get the public timestamp, Cooper needs to create or name a GitHub repo, then run `git remote add origin … && git push -u origin master`. I didn't create repos or touch his GitHub. The rest of the pipeline is not committed, which keeps the commit to what the brief scoped.

## Deviations from the plan, with reasons

1. **Decision 3, professor citation: nothing to transcribe.** The baseline file doesn't mention García-Montalvo, the 1.5M workers, the ~$280, or the $1B claim, so there is no press-coverage wording to fall back on either. I added no claim rows, because putting them in without evidence would be inventing figures. `claim_audit` stays incomplete. The required $420M test passes on fixtures.
2. **Risk to flag:** the frozen config checks that the claim inputs reproduce $420,000,000 within 1%. If the sourced figures turn out different (for example 1.5M × $250), compute stops with a SanityError, and fixing it would mean re-freezing after launch. Capture the claim source soon.
3. **Source URLs:** the baseline file only records a URL for Google Trends. The other 17 rows carry `no URL: none captured in the Nov 18 baseline pull`. They are valid under the schema, but adding real URLs before the Nov 23 render would strengthen the sources line.
4. **Approximate values:** source wording such as "~13%", "~$1.54B" or "3.4M+" is stored as the exact number with the approximation noted in `notes`, because the parser refuses `~` by design.
5. **Preorders anchor:** `preorders_units` / `preorders_usd` point at the latest pre-launch reading (Nov 17, 15.88M / $1.54B), not the brief's older 9.69M. The Nov 10 reading is kept under `_nov10` ids. This is a data choice and can be changed without touching the frozen method.
6. **Evidence matching ignores whitespace only**, exactly as the plan says. Quotes therefore include the markdown `**` where the source bolds them.
7. **PNGs:** each page is screenshotted from its own single-page HTML at 1080×1350. The PDF is printed from the combined HTML.
8. **Additions beyond the plan:** freeze refuses to re-lock; render refuses missing core inputs even with `--allow-partial`; 14 tests beyond the plan's 10.

# Build Brief — GTA VI Launch-Impact Pipeline (EXECUTION)

Cooper approved the plan in `files/PIPELINE-PLAN.md` on Wed Nov 18, 2026, with the recommendations on all eight open questions. Build exactly that plan, with these decisions locked:

## The eight decisions (do not re-open)

1. **Low case:** baseline_daily_absence_rate (sourced) × BambooHR +13% PTO lift, applied to US employed. The +13% is a lift on requests, never an absence rate itself.
2. **High case:** GameSquare's 10% skip rate × full-time employed gamers (defined population). BambooHR's 18% of salaried workers appears only as survey-intent context, never as a model case.
3. **Professor citation:** José García-Montalvo (Pompeu Fabra University) — his 1.5M workers / ~$280 per day inputs enter figures.csv only with an evidence quote from a real source captured in the baseline data file. If the baseline file lacks a citable quote for the claim inputs, use press-coverage wording for the claim and mark the audit inputs as claim-kind figures with their best available source; report exactly what was used.
4. **Output per worker per day:** base = ~$280 (avg annual output ~$70K / 250), matching the claim's own inputs. GDP-per-employed (~$760/day) is the sensitivity case only.
5. **Lock proof:** after the freeze, initialize a git repo in this project folder if none exists, and commit the frozen config + model + lock with a message noting the pre-launch freeze. Then attempt `git push` only if a remote named origin already exists and is authenticated; if no remote exists, create the local commit and report that the GitHub push needs Cooper's repo — do NOT create repos or alter remotes on his GitHub account.
6. **Structured figures block:** define the ```figures block format ingest can read directly, document it in the build report (Muse will update the Nov 20 pull to emit it). Keep hand transcription with evidence quotes as the fallback path.
7. **Super Bowl benchmark:** show absences AND the dollar equivalent at the base output rate.
8. **GTA V 2013 precedent:** include only with a sourced citation in the data; if the baseline data has none, implement the precedent section to render the softened wording ("no dent was reported in contemporary coverage") only when a source row exists, and omit it otherwise. Report which way it landed.

## Scope for this session

1. Build the full pipeline per PIPELINE-PLAN.md (run.py, gta_audit package, templates, tests with fixtures).
2. Run the full test suite. The $420M claim-reproduction test is required and must pass. Any failure: stop, report, do not work around a failing test by weakening it.
3. Baseline transcription + freeze: the baseline pull (scheduled 12:30 PM ET today) writes `hidden_files/data/baseline-2026-11-18.md`. If that file exists when you reach this step, transcribe its figures into data/figures.csv with word-for-word evidence quotes, run ingest, then `run.py freeze`. If it does not exist yet, wait and re-check for up to ~20 minutes; if it still hasn't landed, complete everything else and report the freeze as PENDING on the baseline pull — do not invent figures to freeze with.
4. After a successful freeze: run verify-freeze and record the lock time (ET) and hash prefix. Then the git commit per decision 5.
5. Write `files/BUILD-REPORT.md`: what was built, test results (counts, names), the freeze status + lock details, the structured figures block format, the git/push outcome, and any deviations from the plan with reasons.

## Rules

- Numbers are never invented. A missing input fails loudly.
- Do not modify the scheduled pull jobs or any files outside this project folder.
- Do not touch the live report deliverables (no rendering with real data in this session — fixtures only; the real render is Nov 23).
- Effort: medium. Stop and report on any blocker rather than pushing through.

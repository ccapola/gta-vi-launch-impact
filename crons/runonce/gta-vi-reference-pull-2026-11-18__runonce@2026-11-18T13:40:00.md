---
id: gta-vi-reference-pull-2026-11-18
title: GTA VI report — reference-data pull (professor claim, BLS/BEA/UKG)
enabled: true
owner: goal:gta-vi-launch-impact-report-personal-project
mode: task
schedule:
  kind: runonce
  timezone: America/New_York
  at: 2026-11-18T13:40:00
delivery:
  - chat_id: f8a34614-03d0-4ea6-bea3-e09487f63a3b
metadata:
  tags: [cron:exact-time]
  originating_chat_context_json: '{"chat_id":"f8a34614-03d0-4ea6-bea3-e09487f63a3b","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"728f3881-bf35-3ce7-575e-90fa90e9ccc2"}'
  presentation_locale: en-US
---
Reference-data pull for Cooper's GTA VI launch-impact report. The pipeline is built and the method is frozen (locked Nov 18, 2026, 12:38 PM ET — do NOT re-freeze or modify the frozen config or model). Project folder: ~/workspace/goals/gta-vi-launch-impact-report-personal-project/. The baseline pull (hidden_files/data/baseline-2026-11-18.md) captured none of the model's core reference inputs. Your job: source them properly and load them.

Read first: files/PIPELINE-PLAN.md (dataset schema + model config), files/BUILD-REPORT.md (the structured figures block format and the exact list of missing figure ids), and the pipeline's current data/figures.csv to match its conventions.

Capture these figures, EACH with: value, unit, kind, source name, source URL, and a word-for-word quote from the source that states the figure:
1. The professor claim set: claim_headline_usd ($1B), claim_workers (1.5M), claim_output_per_day (~$280) — attributed to José García-Montalvo, Pompeu Fabra University. Find the best citable source (press coverage quoting his estimate is acceptable; name what it is). If a specific input cannot be sourced, say so plainly in your report — do not paper over it.
2. baseline_daily_absence_rate — the normal share of US workers absent on a typical day (BLS CPS absence data or equivalent).
3. us_employed — current US employment level (BLS).
4. ft_employed_gamers — a sourced basis for the number of full-time employed people who play video games (the GameSquare survey's population or another citable study). If no defensible source exists, report that plainly — the high case stays incomplete rather than getting a made-up base.
5. avg_annual_output_per_worker — the figure behind the ~$70K/yr base in the frozen model; find the closest citable source and name what the figure actually measures (wages vs output).
6. us_gdp_usd — current nominal US GDP (BEA), for the sensitivity case.
7. superbowl_monday_absences_2025 — UKG's survey estimate of planned absences for the Monday after Super Bowl 2025 (~22.6M).
8. GTA V 2013 precedent: a sourced statement on whether the launch showed up in absence/GDP data or contemporary coverage saying no dent was detected. If nothing citable exists, record that plainly (the precedent section will be omitted from the report).
9. Backfill source URLs for the key baseline figures that lack them (BambooHR PTO data, Sensor Tower preorders at minimum) where a real URL exists.

Then:
- Save everything to hidden_files/data/reference-2026-11-18.md, including the structured figures block in the BUILD-REPORT format.
- Transcribe the sourced figures into the pipeline's data/figures.csv with their evidence quotes pointing at the reference file, run the pipeline ingest, then run compute --dry, and run verify-freeze to confirm the freeze is untouched (it must still pass — adding data rows must not alter the frozen files; if verify-freeze fails, STOP and report that immediately).
- Report to Cooper in the main chat (chat_id f8a34614-03d0-4ea6-bea3-e09487f63a3b): which figures were sourced (one line each, with the value), which could NOT be sourced (plainly, with the consequence for the report), and which report sections are now complete per compute --dry. Keep it tight.
- Log a one-line note on tracked item goal_aa1093a9793d.

Rules: no invented numbers, ever; every figure's quote must actually appear in its cited source; if a source can't be reached, write that instead of substituting a guess.

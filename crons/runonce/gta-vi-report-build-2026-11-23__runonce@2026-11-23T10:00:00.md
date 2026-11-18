---
id: gta-vi-report-build-2026-11-23
title: GTA VI report — build and deliver (Mon Nov 23, 10:00 AM)
enabled: true
owner: goal:gta-vi-launch-impact-report-personal-project
mode: task
schedule:
  kind: runonce
  timezone: America/New_York
  at: 2026-11-23T10:00:00
delivery:
  - chat_id: f8a34614-03d0-4ea6-bea3-e09487f63a3b
metadata:
  tags: [cron:exact-time]
  originating_chat_context_json: '{"chat_id":"f8a34614-03d0-4ea6-bea3-e09487f63a3b","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"728f3881-bf35-3ce7-575e-90fa90e9ccc2"}'
  presentation_locale: en-US
---
Build and deliver Cooper's GTA VI launch-impact report. Brief: ~/workspace/goals/gta-vi-launch-impact-report-personal-project/files/GTA-VI-Launch-Impact-Brief.md. Build report and pipeline: ~/workspace/goals/gta-vi-launch-impact-report-personal-project/files/BUILD-REPORT.md and ~/workspace/goals/gta-vi-launch-impact-report-personal-project/pipeline/. Data: ~/workspace/goals/gta-vi-launch-impact-report-personal-project/hidden_files/data/baseline-2026-11-18.md and launchday-2026-11-20.md. If either data file is missing, say so plainly to Cooper and build only from what exists — never fill gaps with invented numbers.

The report is produced BY the pipeline — do not hand-build the report, do not hand-run the model in prose, and do not type numbers into templates. Run the pipeline in this exact order from ~/workspace/goals/gta-vi-launch-impact-report-personal-project/ and stop on any failure, reporting the failure plainly to Cooper instead of working around it:
1. verify-freeze: `python3 pipeline/run.py verify-freeze` — if it fails, the build stops. Record the lock time (ET) and hash prefix it reports.
2. Full tests: `python3 -m unittest discover -s pipeline/tests` — if any test fails, the build stops.
3. ingest: `python3 pipeline/run.py ingest` — this checks figures.csv plus any ```figures blocks in hidden_files/data/*.md against word-for-word evidence quotes, and writes pipeline/data/dataset.json. If ingest fails, the build stops.
4. compute: `python3 pipeline/run.py compute` (you may first run `python3 pipeline/run.py compute --dry` to see which sections are complete or incomplete). Missing core inputs fail loudly — do not invent them.
5. render: `python3 pipeline/run.py render --allow-partial` — partial is allowed only for non-core sections; the pipeline itself refuses to render when core inputs are missing, even with --allow-partial. Render outputs go to ~/workspace/goals/gta-vi-launch-impact-report-personal-project/files/report/ : gta-vi-launch-impact.html, gta-vi-launch-impact.pdf (3 pages, LinkedIn document post), page-1.png, page-2.png, page-3.png, and fact-sheet.json. Check the PNGs and PDF visually before delivering.

Report structure (as rendered by the pipeline): the claim, the audit, the three answers (sick calls, DoorDash, productivity range), the hard anchors (preorders, Twitch peak, TTWO), sources in small print, and the "what we can't measure" line. The pipeline's model is the frozen method locked Nov 18, 2026: absence low/high cases × output per worker per day, producing a defensible range; the viral $1B claim and the ~$420M its own inputs produce next to the model's range; the honest footnote that one-day absence output is mostly deferred, not destroyed (GTA V 2013 precedent section only renders when a sourced precedent row exists).

Methodology note and LinkedIn caption — written from fact-sheet.json ONLY:
6. Write the methodology note (sources, model inputs, limits) as a file in ~/workspace/goals/gta-vi-launch-impact-report-personal-project/files/report/ (alongside the pipeline outputs), using ONLY numbers and facts recorded in ~/workspace/goals/gta-vi-launch-impact-report-personal-project/files/report/fact-sheet.json. Do not quote any number that is not in fact-sheet.json.
7. Draft the LinkedIn caption in Cooper's voice: first-person, direct, leads with the audit finding ("Kalshi is paying $135K for this analysis. I ran my own."), no hype words, no em-dash stuffing. Save it as a file in the same files/report/ folder. Every number in the caption must come from fact-sheet.json only. Cooper posts everything himself — never post to LinkedIn.

Delivery (preserved):
8. Deliver to Cooper in the main chat (chat_id f8a34614-03d0-4ea6-bea3-e09487f63a3b): the headline findings in 3–4 lines (the productivity range vs the $1B claim first), with the report files attached/linked. Log a one-line note on tracked item goal_aa1093a9793d.

Every number in the report, methodology note, and caption must trace to a sourced figure in the data files via the pipeline and fact-sheet.json. If the model can't be run honestly from the data present, deliver the report with that section marked as insufficient data rather than forcing a number — and if the pipeline refuses to render because core inputs are missing, say so plainly to Cooper, list the missing dataset ids the pipeline reports, and do not hand-build a substitute report.

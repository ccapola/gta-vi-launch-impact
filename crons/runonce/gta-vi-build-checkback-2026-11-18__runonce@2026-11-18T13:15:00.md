---
id: gta-vi-build-checkback-2026-11-18
title: GTA VI pipeline — verify build, freeze, and update the pulls
enabled: true
owner: goal:gta-vi-launch-impact-report-personal-project
mode: task
schedule:
  kind: runonce
  timezone: America/New_York
  at: 2026-11-18T13:15:00
delivery:
  - chat_id: f8a34614-03d0-4ea6-bea3-e09487f63a3b
metadata:
  tags: [cron:exact-time]
  originating_chat_context_json: '{"chat_id":"f8a34614-03d0-4ea6-bea3-e09487f63a3b","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"728f3881-bf35-3ce7-575e-90fa90e9ccc2"}'
  presentation_locale: en-US
---
Check back on the Claude Code BUILD session for Cooper's GTA VI launch-impact pipeline (remote-control name "gta-vi-build", running in ~/workspace/goals/gta-vi-launch-impact-report-personal-project/, log at claude-build-session.log in that folder; brief at files/BUILD-BRIEF.md; plan at files/PIPELINE-PLAN.md).

Do this:
1. Read files/BUILD-REPORT.md if it exists, plus the tail of the build log (strip ANSI codes). If the build is still running and no report exists, send Cooper one short line in the main chat (chat_id f8a34614-03d0-4ea6-bea3-e09487f63a3b) saying so, create ONE follow-up runonce check-back 20 minutes later with these same instructions, and stop. Only one such follow-up chain; if the second check also finds it unfinished, report the state plainly and stop.
2. INDEPENDENTLY VERIFY — do not take the report's word: (a) re-run the pipeline test suite yourself (python3 -m unittest discover in the pipeline tests directory, or as the report specifies) and record the real result; (b) if the freeze happened, run the pipeline's verify-freeze and confirm it passes, and note the lock time (ET) and hash prefix; (c) confirm the git commit exists (git log in the project folder). If the freeze is still pending because the baseline data file (hidden_files/data/baseline-2026-11-18.md) landed after the build session gave up waiting, do the transcription + ingest + freeze + verify + git commit yourself exactly as files/BUILD-BRIEF.md scopes it (figures only from that baseline file, word-for-word evidence quotes).
3. Update the two scheduled jobs to the built pipeline: (a) cron gta-vi-launchday-pull-2026-11-20 — add the requirement to ALSO write the structured figures block (format as documented in BUILD-REPORT.md) into its output file, preserving all other instructions; read the job first with cron.view, then cron.update with the complete revised body, then verify with cron.view. (b) cron gta-vi-report-build-2026-11-23 — revise so the report is produced BY the pipeline (verify-freeze → full tests → ingest → compute → render) and the methodology note + LinkedIn caption are written from files/report/fact-sheet.json only; preserve the delivery instructions and the never-invent-numbers rules; same view/update/view verification.
4. Present to Cooper in the main chat: plain-English result — tests (your verified count), freeze status with lock time, git outcome, the two job updates, and any deviation the build reported. Link files/BUILD-REPORT.md. Log a one-line note on tracked item goal_aa1093a9793d.
5. If the interactive build session is idle at its prompt, end it politely (/exit via the process). Never start new build work yourself beyond the freeze completion in step 2.

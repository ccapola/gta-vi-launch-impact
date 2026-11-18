---
id: gta-vi-launchday-pull-2026-11-20
title: GTA VI report — launch-day data pull (Fri Nov 20, 9:30 AM)
enabled: true
owner: goal:gta-vi-launch-impact-report-personal-project
mode: task
schedule:
  kind: runonce
  timezone: America/New_York
  at: 2026-11-20T09:30:00
delivery:
  - chat_id: f8a34614-03d0-4ea6-bea3-e09487f63a3b
metadata:
  tags: [cron:exact-time]
  originating_chat_context_json: '{"chat_id":"f8a34614-03d0-4ea6-bea3-e09487f63a3b","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"728f3881-bf35-3ce7-575e-90fa90e9ccc2"}'
  presentation_locale: en-US
---
Launch-day data pull for Cooper's GTA VI launch-impact report (brief: ~/workspace/goals/gta-vi-launch-impact-report-personal-project/files/GTA-VI-Launch-Impact-Brief.md). GTA VI launched yesterday, Thu Nov 19, 2026. The pre-launch baseline is at ~/workspace/goals/gta-vi-launch-impact-report-personal-project/hidden_files/data/baseline-2026-11-18.md — read it first and use the SAME collection methods so the comparison is apples-to-apples.

Collect and save to ~/workspace/goals/gta-vi-launch-impact-report-personal-project/hidden_files/data/launchday-2026-11-20.md:
1. Google Trends (US) for "call in sick", "sick day", "DoorDash", "GTA 6" for Thu Nov 19, expressed against the baseline Thursdays from the baseline file.
2. GTA VI peak Twitch viewership on Nov 19 (TwitchTracker or similar public source) — the report's hard engagement anchor.
3. Any reported launch-day sales/player numbers from Rockstar, Take-Two, Sony, or credible trackers; Metacritic score as it stands.
4. Day-off tracker updates: any new companies/schools/institutions reported giving Nov 19 off, and any reported sick-day coverage in news.
5. DoorDash proxies: app-store chart movement for DoorDash/Uber Eats, any reported delivery-surge stories.
6. TTWO price action for Nov 19 and this morning.
7. Kalshi album-streams market: any early reported streaming numbers for GTA VI: The Album.

Rules: every figure gets its source named next to it; label proxies as proxies; if a figure can't be verified, say so plainly rather than estimating silently. Log a one-line note on tracked item goal_aa1093a9793d. Then send Cooper ONE short note in the main chat (chat_id f8a34614-03d0-4ea6-bea3-e09487f63a3b): launch-day data is in, the 2–3 headline numbers (Twitch peak, search spike vs baseline, any sales figure), and that the report builds Monday Nov 23. Keep it to a few lines.

ADDITIONAL REQUIREMENT — structured figures block (added Nov 18, 2026 after the pipeline build; format as documented in ~/workspace/goals/gta-vi-launch-impact-report-personal-project/files/BUILD-REPORT.md):
In the SAME output file (~/workspace/goals/gta-vi-launch-impact-report-personal-project/hidden_files/data/launchday-2026-11-20.md), ALSO include a structured figures block that the pipeline's `run.py ingest` can read directly. `run.py ingest` reads every `*.md` in `hidden_files/data/` automatically.

Format — a fenced block exactly like this:
```figures
id,label,value,unit,kind,snapshot,as_of,source_name,source_url,evidence_quote,notes
twitch_peak_nov19,GTA VI peak Twitch viewers (Nov 19),6.2M,count,measured,launchday,2026-11-19,TwitchTracker,https://twitchtracker.com/...,"peaked at 6.2M concurrent viewers",
```

Rules for the block:
- The columns are the figures.csv header minus `evidence_file`, which is set to the file the block sits in. Standard CSV quoting applies.
- `value` must be one clean number: `6.2M`, `$1.54B`, `13%`, `$218.20`, `1,530`. Anything with `~`, `<`, ranges or words is refused. Put "approximately" wording in `notes`.
- `unit` must be one of usd, usd_per_day, count, pct, ratio, index, usd_per_share. `kind` must be one of measured, survey, estimate, proxy, claim, benchmark, precedent. `snapshot` must be one of baseline, launchday, reference. `as_of` uses YYYY-MM-DD.
- `source_url` is a URL, or `no URL: <reason>`.
- `evidence_quote` must appear word for word (whitespace-insensitive) in the same file OUTSIDE the figures block, so a block can never vouch for itself.
- An id defined in both the CSV and a block, or in two blocks, is an error. Nothing is silently overridden.
- Use the frozen ids the config expects for Nov 20: `twitch_peak_nov19`, `ttwo_close_nov19`, `trends_doordash_nov19`.
- Include a row in the block for every launch-day figure you collect that maps to a pipeline dataset id, with its evidence quote also present in the prose of the same file. If a figure cannot be expressed in this clean format, leave it in prose only and say so plainly — do not force or invent a value to fill the block.

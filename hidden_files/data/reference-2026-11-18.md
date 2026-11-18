# GTA VI Launch-Impact — REFERENCE-DATA PULL
**Pulled:** Wednesday, November 18, 2026, ~1:40–2:00 PM EST (America/New_York)
**Purpose:** Source the frozen model's core reference inputs that the 12:30 PM baseline pull did not capture (see files/BUILD-REPORT.md, "Gaps still open"). Every figure below names its source and carries a short verbatim quote from that source. Figures that could not be sourced are recorded as NOT SOURCED, plainly — no substitutes, no estimates.
**Loading:** Sourced figures are in the structured figures block at the end of this file; `run.py ingest` reads it directly (BUILD-REPORT decision 6). The same rows were deliberately NOT duplicated into pipeline/data/figures.csv: the pipeline rejects any id defined in both the CSV and a block as a duplicate. URL backfills for baseline rows were applied to figures.csv directly (§9).

---

## 1. The professor claim set — José García-Montalvo (Pompeu Fabra University)

**Best citable source:** International Business Times UK, "GTA 6 Release Day Set To Cost America $1 Billion With 1.5 Million Workers Plotting a Mass Sick Day," by Jim Manzon, published 07 September 2026, 8:27 AM BST. This is the article that first printed the 1.5 million headcount as García-Montalvo's estimate; US coverage (e.g. iHeart/700WLW, Oct 20, 2026) syndicates the same wording and attributes the analysis to International Business Times.
URL: https://www.ibtimes.co.uk/gta-6-launch-billion-dollar-sick-day-1818190

Verbatim from the article:

> "Around 1.5 million Americans plan to skip work when Grand Theft Auto 6 launches on 19 November, a mass sick day one economist estimates could drain roughly $1 billion (£740 million) from US output in a single day."

> "The estimate comes from José García Montalvo, an economics professor at Pompeu Fabra University in Barcelona."

> "Montalvo bases the figure on roughly 1.5 million absences and an average yearly output of about $70,000 (£51,900) per US worker, landing on a short-term productivity dip of around 2%."

Figures loaded:
- claim_headline_usd = $1B (kind: claim) — quote above.
- claim_workers = 1.5M (kind: claim) — quote above.

**claim_output_per_day — DERIVED, not directly sourced.** No source found states a per-day dollar figure. The article gives only the annual figure ($70,000 per worker per year). The frozen model's $280/day is that annual figure divided by the frozen 250-working-day convention: $70,000 / 250 = $280, and 1.5M × $280 = $420M, the frozen claim-reproduction check. The row is loaded with the $70,000 quote as its evidence and the derivation stated in its notes, so the audit can run — but the report must not present $280/day as a number the professor published. Independent checks agree on the arithmetic: GGRecon (Nov 18, 2026) notes the reported inputs come to "roughly $400 million to $420 million, depending on whether you count 250 or 260 working days"; ThePricer (Nov 16, 2026), using 260 days, gets approximately $404 million.

**Provenance caveat (material to the audit):** the claim's chain is weaker than the coverage suggests. ThePricer's review states the $1 billion figure "is not supported by a published calculation" and that a review of the original reporting "found no published workforce model or study supporting those two claims." Later fact-checks of the original Cadena SER interview (Jul 28, 2025) report that García-Montalvo discussed who might skip work (men 18–30, remote tech workers) but did not give a headcount in that interview; IBTimes UK's own earlier piece (Sep 6, 2026) cautioned against attributing the figures to him as a finding from that interview, one day before the Sep 7 article printed them as his estimate. The rows are therefore loaded as kind=claim with IBTimes UK as the source of record — the claim as printed, not as a verified study.

## 2. baseline_daily_absence_rate — BLS CPS absence rate

**Source:** U.S. Bureau of Labor Statistics, Current Population Survey, Table 47, "Absences from work of employed full-time wage and salary workers by occupation and industry," annual averages 2025 (last modified February 20, 2026).
URL: https://api.bls.gov/cps/cpsaat47.htm

The table's columns are: full-time wage and salary workers (thousands) | absence rate — total, illness or injury, other reasons | lost worktime rate — total, illness or injury, other reasons. The total row reads verbatim:

| Total employed | 121,326 | 3.2 | 2.2 | 1.0 | 1.7 | 1.1 | 0.6 |

So the total absence rate is 3.2% (2.2% illness or injury + 1.0% other reasons); the separate lost-worktime rate is 1.7%. BLS defines the measure verbatim:

> "The absence rate is the ratio of workers with absences to total full-time wage and salary employment."

Figure loaded: baseline_daily_absence_rate = 3.2% (kind: measured).

**Caveats, on the record:** (a) this is a reference-WEEK rate — the share of full-time wage and salary workers with an absence during the survey week — not a directly measured daily rate; the frozen model applies it as the baseline rate, which is the model's stated convention, not a BLS claim. (b) It covers full-time wage and salary workers only (121,326 thousand), excludes the self-employed, and excludes absences for vacation or holidays. (c) The 2025 annual average is an 11-month average excluding October 2025, which was not collected during the federal government shutdown.

## 3. us_employed — BLS employment level

**Source:** U.S. Bureau of Labor Statistics, "The Employment Situation — October 2026," USDL-26-1632, released Friday, November 6, 2026, Summary Table A (household data, seasonally adjusted, numbers in thousands).
URL: https://www.bls.gov/news.release/empsit.htm

Verbatim table lines (columns: Oct. 2025 | Aug. 2026 | Sept. 2026 | Oct. 2026 | change Sept.–Oct. 2026; the Oct. 2025 column is blank in the release because that month was not collected):

| Category | Oct. 2025 | Aug. 2026 | Sept. 2026 | Oct. 2026 | Change |
| Employed | - | 162,746 | 163,152 | 163,615 | 463 |

Figure loaded: us_employed = 163.615M (163,615 thousand, seasonally adjusted, October 2026; kind: measured). This is the household-survey (CPS) employment level — people employed — not the establishment-survey payroll count.

## 4. ft_employed_gamers — NOT SOURCED (high case stays incomplete)

No defensible source for the number of full-time employed people in the US who play video games was found. What exists, and why none of it can carry the frozen model's high case:

- **GameSquare, "The Grand Theft Auto Effect" (ACCESS Newswire, Oct 20, 2026)** defines its population only as a sample. Verbatim: the results came from "a scientific representative sample of 1,000 full time US employees who identified as gamers (with a margin of error of 3%)". The release publishes no population total for full-time employed gamers, and a sample of 1,000 cannot be turned into one without a separate population source. URL: https://www.tradingview.com/news/acceswire%3A491212976094b%3A0-gamesquare-announces-the-grand-theft-auto-effect/
- **ESA Essential Facts** counts all players — "More than 205 million Americans play video games" (2025 report) — including children, retirees, students and part-time workers. It is not a full-time-employed population and cannot be substituted for one.
- The PCMag/YouGov figure sometimes quoted (~12.5M) is an extrapolation of the share of gamers planning time off, not a count of employed gamers, and its population includes students and people without a job that Thursday (ThePricer, Nov 16, 2026, makes the same point).

**Consequence:** no ft_employed_gamers row is loaded. The high absence case (ft_employed_gamers × gamesquare_skip_rate) and both high-case costs stay incomplete, and compute --dry will report absence_cases as INCOMPLETE on this id alone. That is the honest state; the alternative would be inventing the model's largest single input.

## 5. avg_annual_output_per_worker — the ~$70K/yr base figure

**Closest citable source:** Social Security Administration, National Average Wage Index (AWI) series. The series reads verbatim (year, AWI, annual change):

> "2023 66,621.80 4.43% - 2024 69,846.57 4.84% - 2025 72,800.33 4.23%"

URL: https://www.ssa.gov/oact/cola/awiseries.html

Figure loaded: avg_annual_output_per_worker = $69,846.57 (the 2024 AWI, the closest official figure to the claim's ~$70,000; kind: measured). Base rate: $69,846.57 / 250 = $279.39 per day.

**What the figure actually measures — wages, not output.** The AWI is an average WAGE per worker: SSA builds it from wages subject to federal income tax plus deferred compensation, averaged per worker. It is not GDP per worker and not the value of a worker's output (BEA GDP per employed person is roughly $200K/yr — see §6/§3 — which is why the frozen model keeps GDP per employed as the sensitivity case only). Coverage of the claim is inconsistent on exactly this point: IBTimes UK calls the $70,000 "average yearly output," other reports call it salary. The only official ~$70K series that exists is a wage series, and the report's methodology should say so.

## 6. us_gdp_usd — BEA nominal GDP

**Source:** U.S. Bureau of Economic Analysis, "GDP (Advance Estimate), 3rd Quarter 2026," BEA 26-45, released October 29, 2026. The release reports current-dollar GDP growth of 5.6% (annual rate); the level is in BEA's quarterly NIPA file (series A191RC, NIPA Table 1.1.5), summarized verbatim by WhatIsGDP's BEA data page:

> "Current-dollar GDP increased at an annual rate of 5.6 percent to a seasonally adjusted annual rate of $33,010.0 billion."

URLs: https://bea.gov/news/2026/gdp-advance-estimate-3rd-quarter-2026 (release) and https://whatisgdp.com/us-gdp-data (level as published from the BEA file).

Figure loaded: us_gdp_usd = $33.01T (Q3 2026, seasonally adjusted annual rate, advance estimate; kind: measured). Sensitivity rate: $33.01T / 163.615M employed / 250 ≈ $807 per worker-day.

## 7. superbowl_monday_absences_2025 — UKG survey

**Source:** UKG Super Bowl Absenteeism Survey (conducted by The Harris Poll for UKG), as restated on UKG's own blog (Jan 29, 2026):

> "According to UKG's annual Super Bowl Absenteeism Survey, this will surpass last year's record of 22.6 million employees and potentially cost organizations more than $5.2 billion in lost work and productivity."

URL: https://www.ukg.com/blog/operations-leaders/are-you-prepared-super-bowl-monday-absenteeism

Contemporary Feb 2025 coverage of the same survey (Insurance Business, Feb 5, 2025; HR Leader, Feb 7, 2025) reported the same estimate for Monday, February 10, 2025, from a survey of 1,220 employed adults, surpassing the previous record of 18.8 million in 2023. Reuters (Feb 6, 2026) likewise describes "2025's record-setting 22.6 million employees."

Figure loaded: superbowl_monday_absences_2025 = 22.6M (kind: benchmark; a survey estimate of PLANNED absences, extrapolated by UKG — not a count of actual absences).

## 8. GTA V 2013 precedent — NOT LOADED (section omitted by design)

The task for this section was a sourced statement on whether the 2013 launch showed up in absence/GDP data, or contemporary coverage saying no dent was detected. What the search actually found:

- **No BLS or BEA source** — and no contemporary (2013) coverage — stating that GTA V's launch left no dent in absence or GDP data was found. BLS published no such finding; absence data is not produced at a granularity that could isolate one launch day.
- **2026 secondary analyses assert it without citing data.** GTALab (Oct 27, 2026) states: "The U.S. economy's September 2013 GDP figures showed no anomaly attributable to game-launch absenteeism." It cites no BLS table or release for that claim, and it is a 2026 blog assertion, not contemporary coverage and not an official source. Loading it would put an uncited claim about BLS data into a report whose whole point is not doing that.
- **The one sourced 2013 precedent is an intent poll, and it points the other way.** Before GTA V's September 2013 release, IGN polled 10,995 of its readers: "46% said they had booked the day off as holiday, 19% said they would call in claiming to be unwell" (as graded by Vice Atlas, Nov 2026). That is pre-launch intent among a games site's readers — not a measurement, and not evidence of "no dent."
- IBTimes UK's 2013 line — "some reports found up to 6% of workers aged 18 to 35 in cities such as Los Angeles and New York took launch day off" — attributes the figure to unnamed "some reports"; the same line in the 2025 Cadena SER report has been graded unverified by fact-checkers.

**Consequence:** no gtav_2013_precedent row is loaded. Under the frozen config the precedent section renders only when a sourced precedent row exists, so the section will be omitted from the report, exactly as the BUILD-REPORT's landed state anticipated. The brief's "no measurable dent" footnote should be dropped or rewritten to what is actually supported: no official measurement of a GTA V dent exists either way.

## 9. Source-URL backfills applied to pipeline/data/figures.csv

Baseline rows previously carried "no URL: none captured in the Nov 18 baseline pull." Real URLs verified in this pull and written into figures.csv:

- All six BambooHR rows (pto lifts, platform employees, salaried/Gen Z survey rows, survey n) → https://www.bamboohr.com/resources/data-at-work/data-stories/gta-pto (BambooHR, "Gamer's Day Off," Oct 22, 2026 — the page states the 13% lift, the 3.4M+ platform base and the 18% survey figure).
- GameSquare rows (skip rate, considering, survey n) → https://www.tradingview.com/news/acceswire%3A491212976094b%3A0-gamesquare-announces-the-grand-theft-auto-effect/ (the full ACCESS Newswire release).
- Sensor Tower Nov 10 rows (preorders_units_nov10, preorders_usd_nov10) → https://www.talkesport.com/gta-6/gta-6-most-pre-ordered-game-9-69-million-sensor-tower-cyberpunk-2077/ (states the 9.69M / $942M tracker reading and its Nov 10 date).
- Sensor Tower Nov 17 rows (preorders_units, preorders_usd) → https://axis-intelligence.com/gta-6-sales-tracker/ (a tracker mirror reproducing Sensor Tower's dated readings, including Nov 17 at 15.88M; Sensor Tower's own public tracker page URL was not returned by search, so this is a mirror, labeled as such — not sensortower.com itself).
- Left as "no URL": Kalshi forecast, TTWO prices, Logitech day-off rows — no page stating those exact figures was captured in this pull, so no URL was substituted.

```figures
id,label,value,unit,kind,snapshot,as_of,source_name,source_url,evidence_quote,notes
claim_headline_usd,Viral claim: GTA VI launch-day US productivity loss,$1B,usd,claim,reference,2026-09-07,"IBTimes UK, reporting José García-Montalvo (Pompeu Fabra University)",https://www.ibtimes.co.uk/gta-6-launch-billion-dollar-sick-day-1818190,"could drain roughly $1 billion (£740 million) from US output in a single day","Headline claim as printed Sep 7, 2026; no published study or method behind it (see section 1)"
claim_workers,Claim: US workers skipping work on launch day,1.5M,count,claim,reference,2026-09-07,"IBTimes UK, reporting José García-Montalvo (Pompeu Fabra University)",https://www.ibtimes.co.uk/gta-6-launch-billion-dollar-sick-day-1818190,Montalvo bases the figure on roughly 1.5 million absences,"Source wording is roughly 1.5 million; headcount not in the original Cadena SER interview per later fact-checks"
claim_output_per_day,Claim: output per worker per day (derived from the claim's annual figure),$280,usd_per_day,claim,reference,2026-09-07,"IBTimes UK, reporting José García-Montalvo (Pompeu Fabra University)",https://www.ibtimes.co.uk/gta-6-launch-billion-dollar-sick-day-1818190,"an average yearly output of about $70,000 (£51,900) per US worker","DERIVED: $70,000 / 250 working days (frozen convention) = $280; no source states a daily figure directly"
baseline_daily_absence_rate,"BLS absence rate, full-time wage and salary workers (2025 annual average)",3.2%,pct,measured,reference,2025-12-31,"U.S. Bureau of Labor Statistics, CPS Table 47 (annual averages 2025)",https://api.bls.gov/cps/cpsaat47.htm,"Total employed | 121,326 | 3.2 | 2.2 | 1.0 | 1.7 | 1.1 | 0.6","Reference-week rate for full-time wage and salary workers; excludes vacation/holidays and the self-employed; 2025 is an 11-month average excl. Oct 2025"
us_employed,"US employment level, household survey, seasonally adjusted (Oct 2026)",163.615M,count,measured,reference,2026-10-01,"U.S. Bureau of Labor Statistics, Employment Situation — October 2026 (USDL-26-1632), Summary Table A",https://www.bls.gov/news.release/empsit.htm,"Employed | - | 162,746 | 163,152 | 163,615 | 463","163,615 thousand, seasonally adjusted, Oct 2026; table columns are Oct 2025 (not collected), Aug, Sep, Oct 2026"
avg_annual_output_per_worker,Average annual wage per worker (SSA AWI 2024) — closest official figure to the claim's ~$70K,"$69,846.57",usd,measured,reference,2024-12-31,"Social Security Administration, National Average Wage Index (AWI series)",https://www.ssa.gov/oact/cola/awiseries.html,"2024 69,846.57 4.84%","Measures average WAGES per worker (taxable wages plus deferred compensation), NOT output/GDP per worker; 2025 AWI is $72,800.33"
us_gdp_usd,"US nominal (current-dollar) GDP, Q3 2026, seasonally adjusted annual rate (BEA advance estimate)",$33.01T,usd,measured,reference,2026-09-30,"U.S. Bureau of Economic Analysis (BEA), GDP Advance Estimate Q3 2026 (BEA 26-45), NIPA Table 1.1.5",https://bea.gov/news/2026/gdp-advance-estimate-3rd-quarter-2026,"Current-dollar GDP increased at an annual rate of 5.6 percent to a seasonally adjusted annual rate of $33,010.0 billion","Advance estimate released Oct 29, 2026; level from BEA quarterly NIPA file (series A191RC)"
superbowl_monday_absences_2025,Super Bowl Monday 2025 planned absences (UKG survey estimate),22.6M,count,benchmark,reference,2025-02-10,"UKG Super Bowl Absenteeism Survey (The Harris Poll for UKG), via UKG blog",https://www.ukg.com/blog/operations-leaders/are-you-prepared-super-bowl-monday-absenteeism,surpass last year's record of 22.6 million employees,"Survey estimate of planned absences for Mon Feb 10, 2025, extrapolated by UKG; not a count of actual absences"
```

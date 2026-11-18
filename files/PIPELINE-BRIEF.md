# Pipeline Brief — GTA VI Launch-Impact Report

## Context
Cooper is producing an independent audit of the viral claim that GTA VI's launch day (Thu Nov 19, 2026) will cost the US $1 billion in lost productivity. Full project brief: `files/GTA-VI-Launch-Impact-Brief.md` in this folder. The report publishes on LinkedIn early next week as a portfolio piece for Cooper (analyst-track). Credibility is the whole product: every number sourced, the model transparent, the limits stated.

## What to design (PLAN ONLY in this pass — no code, no file writes)

A small, reproducible Python pipeline in this project folder that:

1. **Ingests data snapshots.** Scheduled agent pulls save sourced figures as markdown files under `hidden_files/data/` (baseline today Nov 18, launch-day Fri Nov 20). The pipeline parses or is fed those figures into a single structured dataset (JSON or CSV) where every value carries its source name. Design the schema.
2. **Freezes the model before results.** The productivity model's inputs and formulas are locked in a config file TODAY, before launch-day data exists — the report's credibility claim is "method written before the game launched." Design the config: absence low/high cases, output-per-worker-day values, the comparison benchmarks.
3. **Computes the audit.** The model must reproduce the professor's own-math check: 1.5M workers × ~$280/day ≈ $420M (the $1B claim's inputs don't reach $1B). This reproduction is a required unit test.
4. **Renders the deliverables.** (a) A one-page visual report (HTML → PDF/PNG, LinkedIn document-post format, 3 pages: report visual, model table, methodology). (b) The numbers must come only from the dataset — no hand-typed figures in templates.
5. **Benchmarks to include:** Super Bowl Monday absence estimates (UKG surveys, ~22.6M planned absences in 2025) as the reader-known yardstick; GTA V 2013 launch as the no-measurable-dent precedent.

## Constraints
- Numbers are never invented: a missing input fails loudly, it does not get estimated silently.
- The pipeline runs on this VM with python3; keep dependencies minimal and free (no paid APIs).
- Existing scheduled pulls (Nov 18 baseline, Nov 20 launch-day, Nov 23 report build) are agent tasks that produce the markdown data files; the pipeline consumes them. The Nov 23 build will call the pipeline.
- Effort: medium. One task, this session.

## Plan output required
Files to create (paths), the dataset schema, the model config contents, the render approach, the test list (including the $420M reproduction test), run order for Nov 20 and Nov 23, and open questions for Cooper. Then STOP — execution waits for Cooper's approval.

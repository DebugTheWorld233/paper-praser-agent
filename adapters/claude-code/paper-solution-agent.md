Analyze the target paper and produce a reproduction/improvement planning package.

Arguments:
- `$ARGUMENTS`
- Expected format: `<paper-url-or-local-path> [-- base repo: <repo-url-or-path>] [-- goal: reproduce|improve|audit]`

Follow these instructions:

1. Ensure the current workspace is the root of this repository. If `skills/paper-solution-agent/SKILL.md` or `scripts/paper_source.py` is missing, stop and tell the user to open the `paper-praser-agent` repository root first.
2. Read `skills/paper-solution-agent/SKILL.md` first and follow it as the workflow contract.
3. If the paper source is an arXiv URL/id, direct PDF URL, or local PDF path, run:
   `python scripts/paper_source.py prepare "<paper-source>" --out paper-analysis`
4. Parse the JSON returned by that command. If it contains `analysis_dir`, use that directory for all generated files in this run.
5. If `<analysis_dir>/sources/source_metadata.json` or `<analysis_dir>/sources/paper_text.md` exists, read them before doing additional web lookup.
6. Generate or update the required Chinese Markdown files under `analysis_dir`:
   - `00_MANIFEST.md`
   - `01_PAPER_INFO.md`
   - `02_DATA.md`
   - `03_ENVIRONMENT.md`
   - `04_EXPERIMENT_PLAN.md`
   - `05_ISSUES_AND_ASSUMPTIONS.md`
   - `06_EXECUTION_AND_REVIEW.md`
   - `07_HUMAN_HELP.md`
7. Do not fabricate unavailable facts. Use `BLOCKED` and `NEEDS_HUMAN_CONFIRMATION` where needed.
8. When finished, report:
   - output directory
   - success standard and why
   - top blockers
   - first three implementation steps

---
name: paper-solution-agent
description: "Analyze a target paper and produce a reproduction or improvement solution package. Use when the user asks to analyze a paper, reproduce a paper, turn a paper into an execution plan, inspect paper/code consistency, plan experiments from a paper, identify needed datasets/environment/GPU/human help, or generate paper-analysis documents before implementation."
argument-hint: "[paper-url-or-local-path] [-- base repo: <repo-url-or-path>] [-- goal: reproduce|improve|audit]"
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, WebSearch, WebFetch, Agent, Skill
---

# Paper Solution Agent

Analyze the paper and produce an execution-ready solution package for: **$ARGUMENTS**

## Purpose

Use this skill before implementation when the user has a specific paper and needs a rigorous plan to reproduce, adapt, or improve it. The output is a set of grounded documents, not an experiment run. Do not silently spend GPU budget, call paid APIs, or access restricted data.

## Constants

- **OUTPUT_ROOT = `paper-analysis/`** — root directory for all analysis runs.
- **OUTPUT_DIR = `paper-analysis/<paper-key>/`** — generated documents for one paper go here. For arXiv papers, prefer `first-author-arxiv-id` as `paper-key`. If the directory already exists, add a numeric suffix such as `-2`.
- **OUTPUT_LANGUAGE = `Chinese Markdown`** — write all generated analysis documents in Chinese Markdown by default, even when the paper itself is English. Only switch languages if the user explicitly asks for another output language.
- **DEFAULT_GOAL = `reproduce`** — unless the user asks for improvement, extension, or audit.
- **SUCCESS_STANDARD** — decide and record one of:
  - `code fully aligned`: official code exists, exact benchmark reproduction is feasible, or the user asks for strict replication.
  - `results close enough`: code/data is missing, stochastic training dominates, or implementation must be reconstructed from paper text.
- **BLOCKER_MARKERS = `TODO`, `BLOCKED`, `NEEDS_HUMAN_CONFIRMATION`** — use these exact markers for missing facts.
- **OPENCLAW_MODE** — when running in OpenClaw, treat this `SKILL.md` as a workflow contract instead of a slash command. Prefer file outputs and use `adapters/openclaw/PAPER_SOLUTION_AGENT_PROMPT_CN.md` as the copy-paste entrypoint.

## Inputs

Accept any combination of:

- Paper source: local PDF, arXiv URL/id, DOI URL, project page, or pasted citation.
- Optional code source: official repo, third-party repo, local path, or `base repo: ...`.
- Optional constraints: GPU budget, target OS, target framework, deadline, target figure/table list, or "only plan, no code".

If the paper itself is inaccessible, stop after creating `07_HUMAN_HELP.md` with the exact access request needed.

## Optional Source Preparation Helper

When the project contains `scripts/paper_source.py`, use it before analysis for arXiv URLs, direct PDF URLs, or local PDFs:

```bash
python scripts/paper_source.py prepare "<paper-source>" --out paper-analysis
```

This helper adapts ARIS-style arXiv metadata/PDF download logic, creates a unique run directory, and prints JSON containing `analysis_dir`. Use that `analysis_dir` as `OUTPUT_DIR` for the seven documents. It writes:

- `<analysis_dir>/sources/source_metadata.json`
- `<analysis_dir>/sources/<paper>.pdf`
- `<analysis_dir>/sources/paper_text.md` when PDF text extraction succeeds

If text extraction fails, do not fabricate paper content. Use the PDF directly if the host agent can read PDFs, or record the blocker in `07_HUMAN_HELP.md`.

If the user explicitly requests the legacy flat layout, pass `--flat` and write directly under the supplied `--out` directory.

## Workflow

### Phase 0: Prepare the Workspace

Create `paper-analysis/` if needed. For a new paper, create a fresh run directory using the `<paper-key>` convention. If the same paper key already exists, create `<paper-key>-2`, `<paper-key>-3`, and so on. If a run directory already exists because `scripts/paper_source.py` created it, continue inside that exact directory.

Start `<analysis_dir>/00_MANIFEST.md` with:

```markdown
# Paper Analysis Manifest

**Paper**: [title or source]
**Goal**: reproduce | improve | audit
**Success standard**: code fully aligned | results close enough
**Generated**: [date]

| File | Status | Purpose | Next Action |
|---|---|---|---|
| 01_PAPER_INFO.md | draft | ... | ... |
```

### Phase 1: Load and Ground Sources

Read the paper first. Extract claims from the paper text, not from memory. If the source is a URL and the content cannot be fetched, record the blocker.

If `<analysis_dir>/sources/source_metadata.json` or `<analysis_dir>/sources/paper_text.md` exists, read them before searching the web. Treat extracted text as a convenience source; verify important claims against the PDF/arXiv page when possible.

When code is available:

1. Inspect repository structure, README, requirements, scripts, configs, and result artifacts.
2. Identify the training entrypoint, evaluation entrypoint, dataset loader, and config defaults.
3. Compare implementation details against the paper.

When code is not available:

1. Mark code alignment as unavailable.
2. Derive a reconstruction plan from method, appendix, hyperparameter tables, and experiment sections.
3. Add missing implementation details to `05_ISSUES_AND_ASSUMPTIONS.md`.

### Phase 2: Write the Required Documents

Write all seven required documents. Use concise, evidence-grounded prose. Separate confirmed facts from assumptions.

#### `01_PAPER_INFO.md`

Must contain:

- Paper metadata: title, authors, venue/date if available, links.
- Task definition: input, output, problem setting, constraints.
- Core contribution list: what is new and what is reused.
- Main conclusions: what the paper claims the evidence shows.
- Target metrics: primary and secondary metrics, expected values when known.
- Figures/tables to reproduce: exact IDs, what each shows, required artifacts.
- Reproduction scope: full paper, subset, or figure/table-specific.

#### `02_DATA.md`

Must contain:

- Dataset names and versions.
- Download or access URLs.
- Whether human help is needed and the exact request.
- Raw-to-processed data pipeline.
- Splits, preprocessing, filtering, augmentation, and evaluation labels.
- License, redistribution, commercial-use, privacy, and citation restrictions.
- Expected disk usage for raw, processed, and cached data.

#### `03_ENVIRONMENT.md`

Must contain:

- OS target and known OS assumptions.
- Python, framework, CUDA, cuDNN, compiler, and key library versions.
- Hardware needs: CPU, RAM, GPU type, VRAM, multi-GPU needs.
- Random seeds and determinism controls.
- Expected resource use: disk, GPU memory, runtime, network.
- Installation plan and environment validation commands.

#### `04_EXPERIMENT_PLAN.md`

Must contain:

- Main experiments.
- Ablation experiments.
- Control or comparison experiments.
- For each experiment: purpose, input artifacts, command/config target, expected output file, metrics, and success criterion.
- A decision on whether success means `results close enough` or `code fully aligned`, with rationale.
- Must-run vs optional experiments.

Use this table shape where possible:

```markdown
| ID | Type | Purpose | Inputs | Output | Metric | Success Criterion | Priority |
|---|---|---|---|---|---|---|---|
```

#### `05_ISSUES_AND_ASSUMPTIONS.md`

Must contain:

- What the paper does not specify clearly.
- Where code and paper disagree.
- Supplemental assumptions made by the agent.
- Reason for each assumption or planned change.
- Risk if the assumption is wrong.
- Which assumptions need human confirmation.

Use this table shape:

```markdown
| ID | Issue / Assumption | Evidence | Agent Decision | Reason | Risk | Needs Human? |
|---|---|---|---|---|---|---|
```

#### `06_EXECUTION_AND_REVIEW.md`

Must contain a staged implementation and review plan with verifiable intermediate results.

Required stages:

1. Source acquisition and integrity check.
2. Data download and cleaning.
3. Environment setup.
4. Baseline or official run smoke test.
5. Main training or inference run.
6. Evaluation and table/figure regeneration.
7. Ablation/control runs.
8. Audit and final comparison.

For each stage, specify:

- Goal.
- Concrete steps.
- Expected artifacts.
- Verification method.
- Exit criterion.
- Review risk.

Examples of verifiable intermediate results:

- Data cleaning ends with row counts, checksums, split sizes, and sample previews.
- Environment setup ends with import/version/CUDA checks.
- Training ends with checkpoints and logs.
- Evaluation ends with result JSON/CSV and regenerated table/figure files.

#### `07_HUMAN_HELP.md`

Must contain every item that requires human action or confirmation:

- Closed or license-gated datasets.
- Paid APIs.
- Proprietary software.
- GPU budget approval.
- External network access.
- Paper appendix, supplemental material, or code download permission.
- Accounts, tokens, credentials, or keys that the agent must not guess.
- Paper ambiguities and agent assumptions requiring a human decision.

Use this table shape:

```markdown
| ID | Need | Why It Is Needed | Human Action | Blocking? | Needed By Stage |
|---|---|---|---|---|---|
```

### Phase 3: Cross-Document Consistency Pass

Before finishing:

- Every dataset in `04_EXPERIMENT_PLAN.md` must appear in `02_DATA.md`.
- Every dependency or hardware claim in `04_EXPERIMENT_PLAN.md` must appear in `03_ENVIRONMENT.md`.
- Every unclear or inferred detail must appear in `05_ISSUES_AND_ASSUMPTIONS.md`.
- Every blocker must appear in `07_HUMAN_HELP.md`.
- Every figure/table target in `01_PAPER_INFO.md` must have a path to reproduction or a blocker.
- The manifest must list all seven files and their status.

### Phase 4: Handoff Summary

Report:

- Output directory.
- Success standard and why.
- Top blockers.
- First three implementation steps.
- Whether the package is ready for `/experiment-bridge`, `/run-experiment`, or requires human input first.

## Output Protocols

- Write the generated documents in Chinese Markdown by default. Preserve paper titles, dataset names, method names, metric names, commands, and file paths in their original language when that avoids ambiguity.
- If the user explicitly requests English or another language, follow that request and record the output language in `00_MANIFEST.md`.
- Do not fabricate unavailable facts. Use `BLOCKED` and a human-help item.
- Prefer paper/code citations by file path, section, table, figure, or URL.
- Keep generated documents stable and readable; do not bury blockers in prose.

## Composing With Other Skills

- Use `/experiment-plan` if the user already has a method idea but needs a claim-driven experiment roadmap.
- Use `/experiment-bridge` after this package is ready and implementation should begin.
- Use `/run-experiment` only after data/environment gates pass.
- Use `/experiment-audit` after results exist.
- Use `/paper-writing` only after results and claims are grounded.

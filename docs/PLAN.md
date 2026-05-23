# Paper Solution Agent Implementation Plan

## Goal

Add an ARIS skill that analyzes a target paper and produces an execution-ready solution package for reproducing, adapting, or improving the paper. The package must be explicit about data, environment, experiments, unclear assumptions, staged execution, and required human help.

## Fit With Existing ARIS

ARIS is a Markdown-skill research harness. The clean integration point is a new skill rather than a new runtime service:

- Skill name: `/paper-solution-agent`
- Canonical location: `skills/paper-solution-agent/SKILL.md`
- Codex mirror: `skills/skills-codex/paper-solution-agent/SKILL.md`
- Default output directory when the skill runs: `paper-analysis/`
- Reusable starter template: `templates/PAPER_SOLUTION_AGENT_TEMPLATE_CN.md`

This skill is a pre-experiment planning and audit artifact generator. It can hand off later to `/experiment-bridge`, `/experiment-plan`, `/run-experiment`, `/experiment-audit`, and `/paper-writing`, but it should not silently run expensive experiments.

## Required Output Contract

The skill must create the following files under `paper-analysis/`:

| File | Purpose |
|---|---|
| `00_MANIFEST.md` | Index of all generated artifacts, status, and next actions. |
| `01_PAPER_INFO.md` | Paper metadata, task definition, core contributions, conclusions, target metrics, and figures/tables to reproduce. |
| `02_DATA.md` | Dataset names/versions, download URLs, access blockers, processing plan, licenses, and usage limits. |
| `03_ENVIRONMENT.md` | OS, Python/framework versions, CUDA/cuDNN, key library versions, hardware, seeds, and estimated disk/GPU resources. |
| `04_EXPERIMENT_PLAN.md` | Main experiments, ablations, control experiments, outputs per step, and success criteria. |
| `05_ISSUES_AND_ASSUMPTIONS.md` | Ambiguities in the paper, paper-code mismatch, supplemental assumptions, and reason for each assumption or change. |
| `06_EXECUTION_AND_REVIEW.md` | Phase-by-phase implementation and review plan with verifiable intermediate results for each stage. |
| `07_HUMAN_HELP.md` | Human-help checklist for closed data, paid APIs, proprietary software, GPU budget, network access, permissions, and assumptions requiring confirmation. |

## Workflow Design

1. Load sources
   - Accept paper PDF/arXiv URL/local path, optional official code repo, optional user constraints.
   - Prefer local files if present; use web only when needed for paper/code/data metadata.

2. Extract paper facts
   - Identify paper metadata, task, method, contributions, metrics, datasets, figures/tables, and claimed conclusions.
   - Distinguish facts from inferred assumptions.

3. Inspect code when available
   - Clone/read code only when the user provided a repo or the paper links one.
   - Compare dataset handling, hyperparameters, model architecture, training recipe, evaluation, and missing scripts against the paper.

4. Build the seven documents
   - Write each document with clear TODO/BLOCKED markers where evidence is absent.
   - Include human-help items instead of guessing inaccessible resources.

5. Decide success standard
   - The agent decides whether the target should be "result close enough" or "code fully aligned".
   - Use "code fully aligned" for official benchmark reproduction or when exact code exists.
   - Use "result close enough" for missing code, stochastic training, unavailable data, or implementation-from-paper settings.

6. Present handoff
   - Summarize the first three actionable steps, blockers, and whether the plan is ready for `/experiment-bridge`.

## Implementation Steps

1. Add canonical and Codex mirror skill files.
2. Add a Chinese starter template that users can copy into `paper-analysis/` or use as a reference.
3. Update `templates/README.md` so the template is discoverable.
4. Update `docs/SKILLS_CATALOG.md` and `AGENT_GUIDE.md` so agents route paper-analysis requests to the new skill.
5. Update the Codex mirror skill-count test from 67 to 68.
6. Run targeted tests:
   - `pytest tests/test_codex_skill_mirror.py`
   - If available, a lightweight frontmatter/catalog grep sanity check.

## Success Criteria

- A user can invoke `/paper-solution-agent "<paper url or local path> — base repo: <repo>"`.
- The skill clearly instructs the agent to generate all seven requested documents under `paper-analysis/`.
- Missing data, proprietary dependencies, paid APIs, GPU needs, and unclear paper assumptions are surfaced in `07_HUMAN_HELP.md`.
- The experiment plan separates main, ablation, and control experiments and gives success criteria.
- Codex mirror remains in sync with mainline skills.

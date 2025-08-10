# PROVENANCE

We use AI assistance for scaffolding, docstring drafting, and some utility code. We do **not** ship unreviewed AI output.

## What "AI‑assisted" means here
- Drafts: boilerplate CLI flags, argument parsing, docstrings, tests scaffolds.
- Patterns: standard security patterns (atomic writes, safe extraction, schema‑first JSON).
- Edits: maintainers rework, simplify, and align to repo conventions.

## What is *not* AI‑assisted
- GAP data model, schemas, and validation rules.
- Security policies, threat model choices, and size/time limits.
- Architecture decisions (preview‑secure posture, sim‑only agent).

## Human review & accountability
- Every PR requires *human reviewer sign‑off* (see CODEOWNERS).
- Static analysis: Ruff + Bandit in CI.
- Property‑based tests and unit tests for safety‑critical paths.
- Commit trailers (below) declare whether AI assistance was used.

## Commit trailers
Include one of:
- `Provenance: human-authored`
- `Provenance: AI-assisted, human-reviewed`

Optional:
- `Reviewed-by: @maintainer`
- `Signed-off-by: Name <email>`

## License and originality
All contributed code must be compatible with the repo license. AI suggestions that resemble non‑compatible sources are rejected.

## Why the repo looks "uniformly polished"
- We enforce consistent formatting via **pre‑commit** (Black, Ruff, Docformatter).
- We intentionally wrote security utilities (safe I/O, atomic writes) *first* to keep the preview safe.
- The agent is **simulation-only** and hard‑fails on crypto/upload to avoid giving a false sense of security. 
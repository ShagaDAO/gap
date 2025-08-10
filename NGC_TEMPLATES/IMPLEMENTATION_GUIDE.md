# NGC → GAP/DGN Alignment Implementation Guide

## Quick Overview

This implements the 3-PR plan to make NGC's research-only scope and relationship to GAP/DGN crystal clear.

## PR-A: Repo posture + cross-links

### 1. Replace top of NGC README.md

**Before first heading, add:**
```markdown
[Contents of README_banner.md - the banner and repo map]
```

### 2. Create STATUS.md
```bash
cp NGC_TEMPLATES/STATUS.md ./STATUS.md
```

### 3. Create docs/interop.md  
```bash
mkdir -p docs
cp NGC_TEMPLATES/docs_interop.md ./docs/interop.md
```

**Commit message:**
```
docs: make NGC research-only + wire up GAP/DGN
- README banner + repo map
- STATUS.md (scope & deliverables)  
- docs/interop.md (how NGC consumes GAP / produces DGN samples)
Provenance: AI-assisted, human-reviewed
```

## PR-B: Claims hygiene + context split

### 1. Add context split box to README.md
Near the top of README, after the banner, add:
```markdown
[Contents of context_split_box.md]
```

### 2. Create/update BENCHMARKS.md
```bash
cp NGC_TEMPLATES/BENCHMARKS.md ./BENCHMARKS.md
```

### 3. Update research/energy_economics/README.md
At the top, add:
```markdown
[Contents of corrections_log.md]
```

**Commit message:**
```
docs: separate Shaga production context from NGC research + add explicit targets/corrections
- README context split box
- BENCHMARKS.md target table
- energy_economics corrections log
Provenance: AI-assisted, human-reviewed
```

## PR-C: Light CI to front-run flags

### 1. Create .github/workflows/docs.yml
```bash
mkdir -p .github/workflows
cp NGC_TEMPLATES/docs_ci.yml ./.github/workflows/docs.yml
```

### 2. Create .mlc.config.json
```bash
cp NGC_TEMPLATES/mlc_config.json ./.mlc.config.json
```

**Commit message:**
```
ci: add docs-only gates for links + claims hygiene + cross-repo references
Provenance: AI-assisted, human-reviewed
```

## Optional Tidy-ups

```bash
# Add provenance
cp NGC_TEMPLATES/PROVENANCE.md ./PROVENANCE.md

# Add security policy  
cp NGC_TEMPLATES/SECURITY.md ./SECURITY.md

# Add FAQ
mkdir -p docs
cp NGC_TEMPLATES/docs_faq.md ./docs/faq.md
```

## Test Commands

After implementing, verify:

```bash
# Check links work
grep -q "github.com/ShagaDAO/gap" README.md
grep -q "github.com/ShagaDAO/dgn" README.md

# Check targets label exists
grep -q "engineering targets" BENCHMARKS.md

# Validate markdown (if you have markdownlint)
markdownlint README.md STATUS.md BENCHMARKS.md docs/
```

## Copy-Paste Responses for Critics

- **"Where's the code?"**  
  NGC is a *research* repo. Specs and validators live in GAP (data) and DGN (protocol). NGC consumes GAP and can emit DGN‑conformant samples for analysis.

- **"You claim 2–5 Mbps and ≤50 ms."**  
  Those are **engineering targets** for experimentation. See BENCHMARKS.md. We publish measured results with scripts when ready.

- **"You said 165k users—so it's live?"**  
  Those are Shaga's *classical* streaming stats. Neural codecs are **not** deployed. NGC is research toward that future.

## Result

After these changes:
- ✅ **Contradiction removed:** NGC clearly research-only, production stats labeled as classical streaming
- ✅ **Repos connected:** Clear GAP input → NGC research → DGN output flow  
- ✅ **Audits boring:** CI enforces links + claims hygiene automatically
- ✅ **Future-proof:** Ready for DGN-conformant sample drops when prototypes arrive 
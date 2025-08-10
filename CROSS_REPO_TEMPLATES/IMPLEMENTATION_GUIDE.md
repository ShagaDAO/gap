# 4-Repo Glue Implementation Guide

**Time estimate: ~40 minutes total**

This creates the "obvious story" for GAP → NGC → DGN without you having to explain it every time.

## ✅ 0) Org Front Door (5–10 min)

**Repo:** `github.com/ShagaDAO/.github`  
**File:** `.github/README.md` (creates org profile)

```bash
# In the .github repo
cp CROSS_REPO_TEMPLATES/org_profile_README.md .github/README.md
git add .github/README.md
git commit -m "org: add repo map (GAP → NGC → DGN)"
```

## ✅ 1) GAP Updates (ALREADY DONE)

- ✅ Two-minute tour section added
- ✅ Compatibility matrix added
- Ready to commit:

```bash
git add README.md
git commit -m "docs: add two-minute tour + compatibility matrix

- Links to NGC DGN samples for end-to-end flow
- Shows GAP → NGC → DGN relationship"
```

## 🚧 2) NGC Updates (10–15 min)

**Repo:** `ShagaDAO/ngc`

### A) Add sample files:
```bash
# In NGC repo
mkdir -p samples/dgn
cp CROSS_REPO_TEMPLATES/semantic_update.jsonl samples/dgn/
cp CROSS_REPO_TEMPLATES/residual_chunk.json samples/dgn/
```

### B) Add README section:
Insert the contents of `CROSS_REPO_TEMPLATES/ngc_readme_section.md` into NGC's README.md at an appropriate location.

### C) Commit:
```bash
git add samples/dgn/ README.md
git commit -m "samples: add DGN-shaped output examples (static)

- samples/dgn/semantic_update.jsonl
- samples/dgn/residual_chunk.json  
- README section explaining offline toy pass-through
- Compatibility matrix showing GAP → NGC → DGN flow"
```

## 🚧 3) DGN Updates (10–15 min)

**Repo:** `ShagaDAO/dgn`

### A) Add README section:
Insert the contents of `CROSS_REPO_TEMPLATES/dgn_readme_section.md` into DGN's README.md.

### B) Add cross-repo CI:
```bash
# In DGN repo
mkdir -p .github/workflows
cp CROSS_REPO_TEMPLATES/dgn_crossrepo_ci.yml .github/workflows/crossrepo.yml
```

### C) Commit:
```bash
git add README.md .github/workflows/crossrepo.yml
git commit -m "ci: add cross-repo NGC sample validation

- Two-minute tour showing local + NGC validation
- Weekly CI validates NGC DGN samples
- Compatibility matrix showing consumer relationship"
```

## 🎯 What This Achieves

### Before (confusion):
- "Where's the NGC code?"
- "Is this deployed to 165k users?"
- "How do the repos relate?"

### After (obvious):
1. **Org profile** → "GAP → NGC → DGN" map at first glance
2. **GAP** → "Here's how to validate, and here's the NGC end-to-end example"
3. **NGC** → "Research only, here are static DGN-shaped samples"
4. **DGN** → "Here's how to validate our stuff + NGC's stuff"
5. **CI** → Weekly proof that NGC samples still pass DGN validation

### The Story Writes Itself:
- GAP defines data format ✅
- NGC consumes GAP, produces DGN-shaped samples ✅ (offline/static for now)
- DGN validates those samples ✅ (CI enforced)
- All three repos show the same compatibility matrix ✅

## Test Commands

After implementation:

```bash
# Test GAP README links work
grep -q "github.com/ShagaDAO/ngc" gap/README.md

# Test NGC has DGN samples
ls ngc/samples/dgn/semantic_update.jsonl
ls ngc/samples/dgn/residual_chunk.json

# Test DGN CI references NGC
grep -q "ShagaDAO/ngc" dgn/.github/workflows/crossrepo.yml

# Test compatibility matrices match
grep -A 4 "### Compatibility" gap/README.md
grep -A 4 "### Compatibility" ngc/README.md  
grep -A 4 "### Compatibility" dgn/README.md
```

## Optional Polish (Later)

When you have a spare 30 minutes:
- GAP: Add tiny 5-10s shard as GitHub Release asset
- NGC: Add actual notebook that processes GAP → DGN (replace static files)
- DGN: Add performance benchmarks for NGC samples
- Org: Add badge set (spec-first ✅, validator ✅, research-only, no token)

## Copy-Paste Responses for Critics

After implementation, your standard responses:

- **"Where's the NGC neural codec?"**  
  NGC is research-only. See samples/dgn/ for DGN-shaped outputs that pass validation.

- **"Is this deployed to 165k users?"**  
  Those are Shaga's classical streaming stats. Neural codecs are research (see NGC repo scope).

- **"How do GAP/NGC/DGN relate?"**  
  See ShagaDAO org profile for the one-page map. GAP → NGC → DGN with CI proving the handshake.

The repos become **self-documenting** and **audit-resistant**. 
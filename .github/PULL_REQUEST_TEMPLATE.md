# GAP Pull Request

## Description

Brief description of changes and their motivation.

## Type of Change

- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)  
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📚 Documentation update
- [ ] 🔧 Tooling/infrastructure change

## GAP Specification Changes

- [ ] **Schema version bumped** (if specification changed)
- [ ] **CHANGELOG.md updated** with changes
- [ ] **Backward compatibility** preserved OR migration guide provided
- [ ] **Sample data updated** to reflect specification changes

## Quality Checklist

- [ ] **Validator updated** and tests pass
- [ ] **All samples validate** with new changes
- [ ] **Profile compatibility** maintained (wayfarer-owl)
- [ ] **Documentation updated** for any new features

## Testing

- [ ] **Local validation** run successfully:
  ```bash
  python3 tools/validate.py --profile wayfarer-owl samples/star-atlas_100mb/
  ```
- [ ] **CI checks** pass (GitHub Actions)
- [ ] **Backward compatibility** tested with existing shards

## Data Changes (if applicable)

- [ ] **Data card updated** (docs/data-card.md) if sample data changed
- [ ] **LICENSE-data.md** reviewed for any new data
- [ ] **Privacy implications** considered and documented
- [ ] **File integrity** (SHA-256 hashes) updated

## Additional Notes

Any additional context, testing notes, or considerations for reviewers.

---

By submitting this PR, I confirm:
- [ ] Changes follow GAP design principles (vendor-neutral, open standards)
- [ ] No proprietary or partner-specific dependencies introduced
- [ ] Documentation is clear and complete 
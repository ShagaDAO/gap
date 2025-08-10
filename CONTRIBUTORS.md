# Contributors Guide

**Thank you for your interest in contributing to GAP!**

## How to Contribute

### 📄 **Specification & Documentation**
- Improvements to GAP spec clarity
- Schema enhancements
- Documentation fixes
- Translation contributions

**Process:** Standard GitHub issues + PRs

### 🧰 **Code Contributions**
- Bug fixes in validators or gap-agent
- New profile implementations
- Performance improvements
- Test coverage expansion

**Requirements:**
- All changes must maintain backward compatibility
- Include tests for new features
- Follow existing code style
- Update documentation as needed

### 🎮 **Data Contributions (Invite-Only)**

**Current Status:** Data uploads are **allowlist-only** while we harden anti-sybil defenses.

**Why Allowlist?**
- Prevent fake/duplicate content during early development
- Ensure data quality for initial training runs
- Test anti-sybil detection with known-good contributors

#### Allowlist Application

**To apply for data contribution allowlist:**

📝 **[Apply Here: GitHub Discussions](https://github.com/ShagaDAO/gap/discussions/new?category=allowlist-requests)**

**Requirements:**
- Valid contact information and verification
- Technical capability (describe your setup)
- Hardware specs (GPU model, driver version, OS)
- Bandwidth availability (sustained upload capacity)
- Game access (which titles you can capture)
- Data consent (privacy compliance understanding)

**Hardware Minimums:**
- **GPU:** GTX 1060 / RX 580 or better
- **CPU:** 4+ cores for real-time encode
- **RAM:** 16GB+ for buffering
- **Storage:** 100GB+ free space for local buffering
- **Network:** 10 Mbps+ sustained upload

**What We Provide:**
- Node credentials (scoped, time-limited)
- Technical onboarding session
- Access to private contributor Discord
- Early access to new tools and profiles

#### Data Quality Standards

**Accepted Content:**
- ✅ Original gameplay footage (no streams/videos)
- ✅ Single-player sessions (privacy compliance)
- ✅ Clean captures (no overlays, notifications)
- ✅ Stable framerate (CFR enforced)
- ✅ Synchronized controls (±8ms alignment)

**Rejected Content:**
- ❌ Re-encoded YouTube/Twitch footage
- ❌ Multiplayer with voice chat
- ❌ Content with UI overlays or notifications
- ❌ Duplicate or near-duplicate sessions
- ❌ Synthetic or AI-generated content

#### Contributor Recognition

**Hall of Fame:** Public recognition for high-quality contributors
**Early Access:** New tools and profiles before public release
**Research Credit:** Citation in papers using your data
**Community Role:** Voting on specification changes

## Development Setup

### Local Development

```bash
# Clone and setup
git clone https://github.com/ShagaDAO/gap.git
cd gap

# Install in development mode
pip install -e ./packages/gap-agent[dev]
pip install -r requirements.txt

# Run tests
pytest packages/gap-agent/tests/
python3 tools/validate.py samples/

# Generate synthetic test data
python3 tools/generate_synth_shard.py --duration 30 --output test_shard/
```

### Code Standards

**Python:**
- Black formatting (`black .`)
- Type hints required
- Docstrings for public functions
- Error handling with typed exceptions

**Documentation:**
- Clear examples in docstrings
- Update README for new features
- Schema changes require version bumps

### Testing

**Required Tests:**
- Unit tests for new functions
- Integration tests for CLI commands
- Schema validation tests
- Synthetic data generation tests

**Test Data:**
- Use synthetic data for unit tests
- Never commit real gameplay footage
- Mock external services in tests

## Community Guidelines

### Communication

**GitHub Issues:** Bug reports, feature requests, spec discussions
**Discussions:** General questions, implementation help
**Private Channel:** Allowlisted contributors only (invite-based)

### Code of Conduct

**Expected Behavior:**
- Professional and respectful communication
- Constructive feedback and collaboration
- Respect for intellectual property
- Privacy-conscious development

**Prohibited:**
- Harassment or discriminatory language
- Sharing private/proprietary information
- Circumventing security measures
- Spam or off-topic content

## Roadmap & Priorities

### Current Focus (v0.4.x)
- 🎯 Hardening anti-sybil detection
- 🎯 Profile completeness (Wayfarer-OWL)
- 🎯 Validator stability and performance
- 🎯 Documentation improvements

### Next Phase (v0.5.x)
- 🔮 Additional game profiles
- 🔮 Enhanced encryption options
- 🔮 Improved HF integration
- 🔮 Performance optimizations

### Long Term
- 🌟 Decentralized storage options
- 🌟 Real-time validation
- 🌟 Advanced quality metrics
- 🌟 Cross-platform capture tools

---

**Questions?** Open an issue or join the discussion. We're here to help!

**Ready to contribute data?** [Apply for allowlist access](https://github.com/ShagaDAO/gap/discussions/new?category=allowlist-requests) 
# CI/CD Pipeline Documentation

**Document:** GitHub Actions CI/CD Configuration
**Workflows:** ci.yml, quality-gates.yml, benchmarks.yml
**Status:** ✅ Complete (RC-010)

## Overview

This project uses GitHub Actions for continuous integration and continuous deployment (CI/CD). The pipeline ensures code quality, test coverage, and automated validation for all examples.

**Workflows:**
1. **CI** (`ci.yml`) - Main test and build pipeline
2. **Quality Gates** (`quality-gates.yml`) - Code quality and security checks
3. **Benchmarks** (`benchmarks.yml`) - Performance monitoring (Phase 5 placeholder)

## Workflow Triggers

All workflows trigger on:
- **Push to main** - Validates all changes to the main branch
- **Pull requests** - Validates PRs before merging
- **Manual dispatch** - Can be triggered manually via GitHub UI
- **Schedule** (benchmarks only) - Weekly runs on Sunday at 00:00 UTC

## CI Workflow (ci.yml)

### Purpose
Main testing pipeline that validates Python tests, Rust integration tests, code quality, and documentation.

### Jobs

#### 1. Python Tests
**Duration:** ~3-5 minutes

Runs all Python unit tests across 6 examples:
- example_simple (23 tests)
- example_flags (33 tests)
- example_positional (27 tests)
- example_subcommands (37 tests)
- example_complex (43 tests)
- example_stdlib (29 tests)

**Total:** 192 tests

**Steps:**
1. Setup Python 3.11+
2. Install uv package manager
3. Install project dependencies
4. Run ruff linting
5. Execute pytest for each example with coverage
6. Display test summary

**Success Criteria:**
- All 192 tests pass
- Linting passes with no errors

#### 2. Rust Integration Tests
**Duration:** ~2-3 minutes (if binaries available)

Runs Rust I/O equivalence tests to validate Python-Rust transpilation correctness.

**Steps:**
1. Setup Python 3.11+
2. Setup Rust 1.75+
3. Cache Rust dependencies
4. Check if Rust binaries exist
5. Run cargo test (if binaries available)

**Note:** Binaries require depyler compilation. Tests are skipped if binaries not found.

**Success Criteria:**
- All 38 Rust integration tests pass (if binaries available)
- Clear messaging if binaries missing

#### 3. Code Quality
**Duration:** ~1-2 minutes

Validates code formatting and style.

**Checks:**
- Python formatting (ruff format)
- Type checking (mypy, if configured)
- TODO/FIXME comments (informational)

**Success Criteria:**
- All formatting checks pass
- No blocking style issues

#### 4. Documentation
**Duration:** ~30 seconds

Ensures all documentation is present and up-to-date.

**Checks:**
- README.md exists
- STATUS.md exists
- roadmap.yaml exists
- Each example has README.md
- docs/ directory structure is correct

**Success Criteria:**
- All required documentation files present

#### 5. Final Status Check
**Duration:** ~5 seconds

Aggregates results from all previous jobs.

**Success Criteria:**
- Python tests: ✅ Success
- Code quality: ✅ Success
- Documentation: ✅ Success
- Rust tests: ✅ Success or ⚠️ Skipped

## Quality Gates Workflow (quality-gates.yml)

### Purpose
Comprehensive code quality, security, and complexity analysis.

### Jobs

#### 1. PMAT Quality Gates
**Duration:** ~1-2 minutes

Runs PMAT (PAIML MCP Agent Toolkit) quality analysis.

**Checks:**
- Technical Debt Gradient (TDG) scoring
- Quality gate thresholds
- Generates TDG report artifact

**Note:** Non-blocking. Skips gracefully if pmat not installed.

#### 2. Test Coverage Report
**Duration:** ~3-4 minutes

Generates comprehensive test coverage report.

**Metrics:**
- Line coverage
- Branch coverage
- Function coverage

**Target:** 100% coverage across all examples

**Artifacts:**
- coverage.xml (uploadable to Codecov, Coveralls, etc.)

#### 3. Complexity Analysis
**Duration:** ~30 seconds

Analyzes code complexity using radon.

**Metrics:**
- Cyclomatic complexity (target: ≤10)
- Maintainability index
- Per-function complexity scores

#### 4. Security Scan
**Duration:** ~1 minute

Scans for security vulnerabilities.

**Checks:**
- Known CVEs in dependencies (safety)
- Potential secrets in code (grep patterns)
- API keys, passwords, tokens

**Note:** Informational, does not block CI

#### 5. Dependency Audit
**Duration:** ~1-2 minutes

Audits Python and Rust dependencies.

**Tools:**
- pip-audit (Python)
- cargo-audit (Rust)

**Checks:**
- Vulnerable dependencies
- Outdated packages
- License compliance

#### 6. Performance Linting
**Duration:** ~30 seconds

Checks for performance anti-patterns.

**Checks:**
- Inefficient string concatenation
- Excessive list comprehensions
- N+1 query patterns

#### 7. Quality Summary
Aggregates all quality gate results.

## Benchmarks Workflow (benchmarks.yml)

### Purpose
Performance monitoring and regression detection.

**Current Status:** Phase 5 placeholder

### Jobs

#### 1. Benchmark Infrastructure Check
**Duration:** ~10 seconds

Reports status of benchmarking infrastructure.

**Information:**
- Planned benchmarks (microbenchmarks, macro benchmarks)
- Expected performance targets
- Implementation roadmap (RC-013 through RC-018)

#### 2. Quick Performance Check
**Duration:** ~1 minute

Runs basic startup time tests.

**Tests:**
- Python script startup time
- Average over 10 executions
- Per-example results

**Note:** Rough estimates only. Full benchmarking in Phase 5.

#### 3. Memory Usage Check
**Duration:** ~30 seconds

Basic memory usage information.

**Note:** Detailed profiling planned for Phase 5.

#### 4. Benchmark Summary
Aggregates benchmark results and shows next steps.

## Badge Configuration

Add these badges to README.md:

```markdown
![CI](https://github.com/YOUR_USERNAME/reprorusted-python-cli/workflows/CI/badge.svg)
![Quality Gates](https://github.com/YOUR_USERNAME/reprorusted-python-cli/workflows/Quality%20Gates/badge.svg)
![Benchmarks](https://github.com/YOUR_USERNAME/reprorusted-python-cli/workflows/Benchmarks/badge.svg)
```

## Local Testing

### Run CI checks locally

```bash
# Python tests
uv run pytest examples/ -v --cov

# Linting
uv run ruff check .
uv run ruff format --check .

# Type checking
uv run mypy examples/

# Rust tests (requires binaries)
cargo test --test test_io_equivalence
```

### Run quality gates locally

```bash
# PMAT analysis (if installed)
pmat analyze tdg

# Complexity analysis
pip install radon
radon cc examples/ -a -nb
radon mi examples/ -nb

# Security scan
pip install safety
safety check

# Dependency audit
pip install pip-audit
pip-audit
cargo audit
```

## Troubleshooting

### Python Tests Failing

**Issue:** Tests fail in CI but pass locally

**Solutions:**
1. Check Python version consistency (3.11+)
2. Ensure all dependencies in pyproject.toml
3. Check for environment-specific issues
4. Review test logs in GitHub Actions

### Rust Tests Skipped

**Issue:** "Rust binaries not found" message

**Expected Behavior:** This is normal if binaries not committed

**To fix:**
1. Install depyler locally
2. Run `make compile` in each example directory
3. Commit binaries (optional, large files)
4. Or skip Rust tests in CI (they're validated locally)

### Quality Gates Failing

**Issue:** Quality gate warnings or failures

**Solutions:**
1. Review TDG report artifact
2. Address high-complexity functions
3. Fix linting issues
4. Update dependencies if vulnerable

### Slow CI Runs

**Issue:** CI takes >10 minutes

**Solutions:**
1. Enable caching (already configured for Rust)
2. Parallelize jobs where possible
3. Skip optional checks (benchmarks)
4. Optimize test suite

## CI/CD Best Practices

### 1. Fast Feedback
- **Target:** <5 minutes for main CI
- **Target:** <30 seconds for pre-commit checks
- **Current:** ~5-7 minutes (within target)

### 2. Fail Fast
- Critical jobs (python-tests) run first
- Dependent jobs (rust-tests) run after
- Quality gates run in parallel

### 3. Clear Messaging
- Descriptive job names
- Emoji indicators (✅❌⚠️ℹ️)
- Helpful error messages

### 4. Caching
- Rust dependencies cached
- Python virtual environments created fresh (uv is fast)

### 5. Artifacts
- TDG reports saved for analysis
- Coverage reports uploadable to external services

## Integration with GitHub

### Branch Protection Rules

Recommended settings:
```yaml
Require status checks to pass before merging:
  ✅ CI / Python Tests
  ✅ CI / Code Quality
  ✅ CI / Documentation
  ⚠️ CI / Rust Tests (optional)

Require branches to be up to date before merging: ✅
```

### Pull Request Template

Create `.github/pull_request_template.md`:

```markdown
## Description
<!-- Describe your changes -->

## Testing
- [ ] All Python tests pass locally
- [ ] Linting passes (ruff check .)
- [ ] Documentation updated
- [ ] Rust binaries compiled (if applicable)

## Checklist
- [ ] Tests added for new functionality
- [ ] README updated if needed
- [ ] STATUS.md updated
- [ ] Commits follow conventional format
```

## Future Enhancements

### Phase 5: Full Benchmarking (Planned)

When benchmarking infrastructure is complete (RC-013 through RC-018):

1. **Automated benchmarks** on every PR
2. **Performance regression detection**
3. **Historical performance tracking**
4. **Comparison charts** (Python vs Rust)
5. **Memory profiling** with detailed reports

### Additional Workflows (Potential)

1. **Dependency Update** - Automated dependency updates
2. **Release** - Automated versioning and releases
3. **Deploy Docs** - GitHub Pages deployment
4. **Notification** - Slack/Discord notifications

## Monitoring and Alerts

### GitHub Actions Dashboard

View workflow runs:
```
https://github.com/YOUR_USERNAME/reprorusted-python-cli/actions
```

### Success Metrics

Track these metrics over time:
- CI pass rate (target: >95%)
- Average CI duration (target: <5 minutes)
- Test coverage (target: 100%)
- TDG score (target: >90/100)

### Alert Conditions

Set up notifications for:
- ❌ CI failures on main branch
- ⚠️ Quality gate degradation
- 🐌 CI duration >10 minutes
- 📉 Coverage drops <100%

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [uv Package Manager](https://github.com/astral-sh/uv)
- [Rust Actions](https://github.com/actions-rs)
- [pytest Documentation](https://docs.pytest.org/)
- [cargo test Documentation](https://doc.rust-lang.org/cargo/commands/cargo-test.html)

---

**Implementation:** RC-010
**Workflows:** 3 (ci.yml, quality-gates.yml, benchmarks.yml)
**Jobs:** 15 total across all workflows
**Target Duration:** <10 minutes end-to-end
**Quality:** Production-ready with comprehensive checks

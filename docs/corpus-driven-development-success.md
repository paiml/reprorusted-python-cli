# Corpus-Driven Development Success Story

**Date:** 2025-11-30
**Project:** reprorusted-python-cli data science pipeline
**Impact:** Drove depyler from 44% to 78.1% transpilation, targeting 80% single-shot compile

## Executive Summary

This corpus and its data science pipeline transformed depyler development from intuition-driven to data-driven. By applying Tarantula fault localization, weak supervision labeling, and single-shot compile analysis, we created an actionable roadmap that improved depyler's success rate by +34.1%.

## The Challenge

Depyler could transpile Python to Rust, but which features should be prioritized? With hundreds of potential improvements, how do you maximize impact?

**Initial State:**
- 44% transpilation rate
- 30 categories with zero success
- No visibility into what actually compiles

## Methodology

### 1. Tarantula Fault Localization

We applied the Tarantula algorithm from software fault localization research to identify which Python features most strongly correlated with transpilation failures.

```
Feature              Suspiciousness   Impact
---------------------------------------------
async_await          0.946            HIGH
generator            0.927            HIGH
walrus_operator      0.850            MEDIUM
lambda               0.783            MEDIUM
context_manager      0.652            MEDIUM
```

**Insight:** async_await identified as #1 priority - this drove depyler to ship async with/for support.

### 2. Single-Shot Compile Analysis

We discovered a critical gap: 78% of files transpiled, but only 24% actually compiled with `cargo check`.

```
+-------------------------------------------+
| Transpilation:     78.1%  (473/606)       |
| Single-shot:       24%    (31/128)        |
| Gap:               54%    <- Hidden debt  |
+-------------------------------------------+
```

This shifted focus from "more transpilation" to "better Rust quality."

### 3. Error Pattern Mining

Analyzing `cargo check` failures revealed quick wins:

| Error | Files | Fix |
|-------|-------|-----|
| `main() -> i32` | 6 | Return `()` not `i32` |
| `os` not found | 5 | Map os module |
| `Callable` type | 4 | Map to `fn()` |
| `time`/`date` | 6 | Datetime mapping |

**Result:** Created roadmap for +21 files (24% -> 40% projected).

### 4. Weak Supervision Labeling

Programmatic labeling classified 606 samples by risk:

- **HIGH_RISK**: 23 samples (async, generators)
- **MEDIUM_RISK**: 133 samples (context managers, classes)
- **LOW_RISK**: 450 samples (basic operations)

This automated triage of what to fix first.

## Toolchain

```bash
# Retranspile with latest depyler
make corpus-retranspile

# Run full analysis pipeline
make corpus-pipeline

# Check for regressions in CI
make corpus-ci

# Measure single-shot compile rate
make corpus-e2e-rate

# Get prioritized recommendations
make corpus-recommendations

# View unified dashboard
make corpus-dashboard
```

## Results

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Transpilation | 44% | 78.1% | +34.1% |
| Zero-success categories | 30 | 0 | -30 |
| Single-shot compile | ~10% | 24% | +14% |
| Release gate | N/A | 80% target | Tracking |

## Key Insights

1. **Measure what matters**: Transpilation % alone was misleading. Single-shot compile rate revealed the real gap.

2. **Data beats intuition**: Tarantula identified async as #1 priority, not the obvious suspects.

3. **Quick wins exist**: Simple fixes like `main() -> i32` unlocked +6 files instantly.

4. **CI prevents regression**: Automated validation catches breakages before release.

## GitHub Issues Created

- [#193 - Track single-shot compile rate](https://github.com/paiml/depyler/issues/193)
- [#194 - Release gate: 80% single-shot compile](https://github.com/paiml/depyler/issues/194)
- [#195-198 - Quick win roadmap](https://github.com/paiml/depyler/issues/195)

## Reproduction

```bash
git clone https://github.com/paiml/reprorusted-python-cli
cd reprorusted-python-cli
make install
make corpus-dashboard
```

## Architecture

```
reprorusted-python-cli/
+-- data/
|   +-- depyler_citl_corpus_v2.parquet  # Source corpus with Tarantula insights
|   +-- labeled_corpus.parquet           # Weak supervision labels
|   +-- ci_baseline.json                 # CI regression baseline
+-- scripts/
|   +-- label_corpus.py                  # Weak supervision labeling
|   +-- augment_corpus.py                # Data augmentation
|   +-- corpus_quality_report.py         # Quality metrics
|   +-- ci_runner.sh                     # CI validation
+-- .github/workflows/
|   +-- corpus-validation.yml            # GitHub Actions CI
```

## Related Documentation

- [Corpus Improvement Analysis](./corpus-improvement-analysis.md) - Initial gap analysis
- [Tarantula Documentation](./corpus-extraction.md) - Fault localization details
- [CI/CD Integration](./ci-cd.md) - Automated validation

---

*This success story demonstrates how a data-driven corpus can transform compiler development priorities.*

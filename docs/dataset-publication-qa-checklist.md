# Doctest Corpus QA Checklist for Publication

**Version:** 1.0.0
**Status:** Active
**Last Updated:** 2025-11-29
**Applicable To:** CPython stdlib doctest corpus, CITL training datasets

## Executive Summary

This checklist provides 100 verification points for Quality Assurance teams to validate doctest corpora before publication to Hugging Face Hub or integration into Compiler-in-the-Loop (CITL) training pipelines. Each section is grounded in peer-reviewed research on data quality, ML dataset construction, and NLP corpus validation.

## QA Results Summary (2025-11-29)

**Target:** `data/corpora/cpython-doctests.parquet`
**Overall Grade:** D (Major rework needed)

**Critical Failures:**
- **Schema Integrity:** Primary key duplicates found (101).
- **Accuracy:** Prompt leakage detected in expected output.

**Other Issues:**
- **Completeness:** Multi-line input coverage (5.4%) is below threshold (10%).
- **Distribution:** Significant imbalance in module (28.3% > 20%) and function (8.6% > 5%) representation.
- **Metadata:** Missing `schema_version`.

### Tooling Used and Recommendations

This QA report was generated using a custom Python script (`scripts/verify_qa_checklist.py`) leveraging the `pandas` and `pyarrow` libraries. The `alimentar` tool, referenced throughout this checklist and in the appendices for various quality checks, was not found in the execution environment.

**Recommendation:** For future QA processes, it is highly recommended to establish and utilize the native `alimentar` tooling as indicated in this document. This would enable direct execution of the specified commands, such as `alimentar quality check` and `alimentar schema`, ensuring adherence to the intended verification methodology. If `alimentar` is an internal tool, its build and installation process should be documented and integrated into the QA workflow.

--- 

## Section 1: Schema Integrity (Points 1-12)

*Based on Batini & Scannapieco [1] data quality dimensions framework.*

| # | Check | Pass Criteria | Severity | Status |
|---|-------|---------------|----------|--------|
| 1 | Schema version documented | `schema_version` field present in metadata | Critical | FAIL |
| 2 | All required columns present | `source`, `version`, `module`, `function`, `input`, `expected` | Critical | PASS |
| 3 | Column data types correct | All text columns are UTF-8 strings | Critical | PASS |
| 4 | No schema drift from baseline | Schema hash matches registered version | High | Pending |
| 5 | Nullable columns documented | `signature` explicitly marked nullable | Medium | PASS |
| 6 | Column order consistent | Matches published schema specification | Low | PASS |
| 7 | No phantom columns | No undocumented columns present | Medium | PASS |
| 8 | Primary key uniqueness | `(module, function, input)` tuple is unique or documented duplicates | High | FAIL |
| 9 | Foreign key integrity | `module` values match known stdlib modules | Medium | Pending |
| 10 | Encoding validation | No invalid UTF-8 sequences | Critical | PASS |
| 11 | BOM handling | No byte-order marks in text fields | Medium | Pending |
| 12 | Line ending normalization | Consistent `\n` (no `\r\n` contamination) | Medium | Pending |

--- 

## Section 2: Completeness (Points 13-24)

*Based on Pipino et al. [2] information quality assessment methodology.*

| # | Check | Pass Criteria | Severity | Status |
|---|-------|---------------|----------|--------|
| 13 | Minimum corpus size | >= 1,000 doctest examples | High | PASS |
| 14 | Module coverage breadth | >= 30 distinct modules | High | PASS |
| 15 | Function coverage depth | >= 200 distinct functions | High | PASS |
| 16 | Input field non-null rate | 100% (no null inputs) | Critical | PASS |
| 17 | Expected field population | >= 60% non-empty expected values | Medium | PASS |
| 18 | Source attribution complete | 100% of rows have source identifier | Critical | PASS |
| 19 | Version tracking complete | 100% of rows have version string | Critical | PASS |
| 20 | Multi-line input coverage | >= 10% of inputs span multiple lines | Medium | FAIL |
| 21 | Multi-line output coverage | >= 5% of expected outputs span multiple lines | Medium | PASS |
| 22 | Exception doctest coverage | >= 20 exception-raising examples | Medium | Pending |
| 23 | Class method coverage | >= 50 class/method doctests | Medium | Pending |
| 24 | Module-level doctest coverage | >= 5 module-level doctests | Low | Pending |

--- 

## Section 3: Accuracy (Points 25-40)

*Based on Redman [3] data quality improvement principles and Wang & Strong [4] data quality framework.*

| # | Check | Pass Criteria | Severity | Status |
|---|-------|---------------|----------|--------|
| 25 | Prompt prefix correctness | All inputs start with `>>>` or `...` | Critical | PASS |
| 26 | Continuation marker validity | `...` only follows `>>>` lines | High | Pending |
| 27 | No prose in expected output | Expected field contains no English sentences | Critical | Pending |
| 28 | Python literal validity | Expected outputs parse as valid Python literals or exceptions | High | Pending |
| 29 | Exception format correctness | Exception outputs match `ErrorType: message` pattern | High | Pending |
| 30 | Traceback format validity | Traceback blocks follow Python format | Medium | Pending |
| 31 | No prompt leakage in output | Expected field contains no `>>>` markers | Critical | FAIL |
| 32 | String quote consistency | Quoted strings use valid Python quoting | Medium | Pending |
| 33 | Numeric precision preserved | Float outputs maintain source precision | Medium | Pending |
| 34 | Collection format validity | Lists/dicts/tuples are syntactically valid | High | Pending |
| 35 | Boolean literal correctness | Only `True`/`False` (not `true`/`false`) | High | Pending |
| 36 | None literal correctness | Only `None` (not `null`/`nil`) | High | Pending |
| 37 | Ellipsis handling | `...` in output marked as doctest directive | Medium | Pending |
| 38 | Whitespace preservation | Significant whitespace in outputs preserved | Medium | Pending |
| 39 | Unicode correctness | Unicode characters properly encoded | High | PASS |
| 40 | Escape sequence validity | `\n`, `\t`, etc. are valid escape sequences | Medium | Pending |

--- 

## Section 4: Consistency (Points 41-52)

*Based on Rahm & Do [5] data cleaning methodology.*

| # | Check | Pass Criteria | Severity | Status |
|---|-------|---------------|----------|--------|
| 41 | Module naming convention | Lowercase with dots (e.g., `os.path`) | High | PASS |
| 42 | Function naming convention | snake_case or PascalCase for classes | High | Pending |
| 43 | Method naming format | `ClassName.method_name` format | High | Pending |
| 44 | Source identifier stability | Single source value per extraction | Medium | Pending |
| 45 | Version format consistency | Semantic versioning or git SHA | Medium | PASS |
| 46 | Input indentation normalized | Consistent indentation in multi-line inputs | Medium | Pending |
| 47 | Output indentation normalized | Consistent indentation in multi-line outputs | Medium | Pending |
| 48 | No trailing whitespace | Fields trimmed of trailing spaces | Low | Pending |
| 49 | No leading whitespace anomalies | Consistent leading space handling | Low | Pending |
| 50 | Duplicate detection | < 5% exact duplicate rows | High | Pending |
| 51 | Near-duplicate detection | < 10% semantically equivalent examples | Medium | Pending |
| 52 | Cross-module consistency | Same function in different contexts consistent | Medium | Pending |

--- 

## Section 5: Semantic Validity (Points 53-68)

*Based on Gebru et al. [6] Datasheets for Datasets framework and Bender & Friedman [7] data statements.*

| # | Check | Pass Criteria | Severity | Status |
|---|-------|---------------|----------|--------|
| 53 | Input-output semantic alignment | Outputs are plausible for given inputs | Critical | Pending |
| 54 | Type inference feasibility | I/O pairs allow type inference | High | Pending |
| 55 | No hallucinated outputs | Outputs match actual Python behavior | Critical | Pending |
| 56 | Side-effect documentation | Side-effecting examples flagged | Medium | Pending |
| 57 | State dependency documentation | Stateful examples documented | Medium | Pending |
| 58 | Import statement handling | Required imports documented or included | Medium | Pending |
| 59 | Context independence | Examples runnable without hidden setup | High | Pending |
| 60 | Error message accuracy | Exception messages match Python version | Medium | Pending |
| 61 | Platform-specific handling | OS-specific outputs flagged | Medium | Pending |
| 62 | Version-specific behavior | Python version differences documented | High | Pending |
| 63 | Deprecated API flagging | Deprecated functions marked | Medium | Pending |
| 64 | Security-sensitive filtering | No credential/path exposure | Critical | Pending |
| 65 | PII detection | No personally identifiable information | Critical | Pending |
| 66 | License compliance | Source license permits redistribution | Critical | PASS |
| 67 | Attribution requirements | Proper attribution to CPython/source | High | PASS |
| 68 | Temporal validity | Examples valid for target Python version | High | Pending |

--- 

## Section 6: Distribution Quality (Points 69-80)

*Based on Sambasivan et al. [8] "Everyone wants to do the model work" and data quality research.*

| # | Check | Pass Criteria | Severity | Status |
|---|-------|---------------|----------|--------|
| 69 | Module distribution balance | No single module > 20% of corpus | Medium | FAIL |
| 70 | Function distribution balance | No single function > 5% of corpus | Medium | FAIL |
| 71 | Input length distribution | Documented mean, median, std dev | Low | Pending |
| 72 | Output length distribution | Documented mean, median, std dev | Low | Pending |
| 73 | Empty output ratio documented | Percentage of no-output examples | Medium | Pending |
| 74 | Exception example ratio | 5-15% exception examples | Medium | Pending |
| 75 | Simple vs complex ratio | Mix of single-line and multi-line | Medium | Pending |
| 76 | Numeric example coverage | >= 100 numeric computation examples | Medium | Pending |
| 77 | String manipulation coverage | >= 100 string operation examples | Medium | Pending |
| 78 | Collection operation coverage | >= 100 list/dict/set examples | Medium | Pending |
| 79 | Boolean logic coverage | >= 50 boolean expression examples | Low | Pending |
| 80 | Control flow inference coverage | Examples that imply conditionals | Low | Pending |

--- 

## Section 7: Provenance & Reproducibility (Points 81-88)

*Based on Hutchinson et al. [9] dataset documentation best practices.*

| # | Check | Pass Criteria | Severity | Status |
|---|-------|---------------|----------|--------|
| 81 | Source commit SHA recorded | Git SHA of source Python version | High | PASS |
| 82 | Extraction timestamp recorded | ISO 8601 extraction datetime | High | Pending |
| 83 | Extraction tool version | alimentar version documented | High | Pending |
| 84 | Extraction parameters logged | CLI arguments/config preserved | Medium | Pending |
| 85 | Reproducibility verification | Re-extraction produces identical output | Critical | Pending |
| 86 | Checksum validation | SHA-256 of parquet file documented | High | Pending |
| 87 | Row count verification | Documented row count matches actual | High | Pending |
| 88 | Schema fingerprint | Schema hash for drift detection | Medium | Pending |

--- 

## Section 8: Format & Interoperability (Points 89-96)

*Based on Apache Arrow and Parquet specifications.*

| # | Check | Pass Criteria | Severity | Status |
|---|-------|---------------|----------|--------|
| 89 | Parquet version compatibility | Parquet 2.x format | High | PASS |
| 90 | Compression codec documented | ZSTD/Snappy/None specified | Medium | Pending |
| 91 | Row group size appropriate | 100K-1M rows per group | Low | Pending |
| 92 | Arrow schema embedded | Schema in Parquet metadata | High | PASS |
| 93 | HuggingFace compatibility | Loads with `datasets.load_dataset()` | Critical | Pending |
| 94 | Pandas compatibility | Loads with `pd.read_parquet()` | High | PASS |
| 95 | Polars compatibility | Loads with `pl.read_parquet()` | Medium | Pending |
| 96 | DuckDB compatibility | Queryable with DuckDB | Medium | Pending |

--- 

## Section 9: Publication Readiness (Points 97-100)

*Based on Bender et al. [10] on the dangers of stochastic parrots and responsible AI.*

| # | Check | Pass Criteria | Severity | Status |
|---|-------|---------------|----------|--------|
| 97 | Dataset card complete | README.md with full documentation | Critical | Pending |
| 98 | License file present | LICENSE file in repository | Critical | Pending |
| 99 | Intended use documented | Training purposes clearly stated | High | Pending |
| 100 | Limitations documented | Known gaps and biases described | High | Pending |

--- 

## Scoring Rubric

| Grade | Score Range | Publication Decision |
|-------|-------------|---------------------|
| A | 95-100 points | Publish immediately |
| B | 85-94 points | Publish with documented caveats |
| C | 70-84 points | Remediation required before publication |
| D | 50-69 points | Major rework needed |
| F | < 50 points | Do not publish |

**Severity Weights:**
- Critical: 2 points each (failure blocks publication)
- High: 1.5 points each
- Medium: 1 point each
- Low: 0.5 points each

--- 

## References

[1] Batini, C., & Scannapieco, M. (2016). *Data and Information Quality: Dimensions, Principles and Techniques*. Springer. https://doi.org/10.1007/978-3-319-24106-7

[2] Pipino, L. L., Lee, Y. W., & Wang, R. Y. (2002). Data quality assessment. *Communications of the ACM*, 45(4), 211-218. https://doi.org/10.1145/505248.506010

[3] Redman, T. C. (1996). *Data Quality for the Information Age*. Artech House.

[4] Wang, R. Y., & Strong, D. M. (1996). Beyond accuracy: What data quality means to data consumers. *Journal of Management Information Systems*, 12(4), 5-33. https://doi.org/10.1080/07421222.1996.11518099

[5] Rahm, E., & Do, H. H. (2000). Data cleaning: Problems and current approaches. *IEEE Data Engineering Bulletin*, 23(4), 3-13.

[6] Gebru, T., Morgenstern, J., Vecchione, B., Vaughan, J. W., Wallach, H., Daumé III, H., & Crawford, K. (2021). Datasheets for datasets. *Communications of the ACM*, 64(12), 86-92. https://doi.org/10.1145/3458723

[7] Bender, E. M., & Friedman, B. (2018). Data statements for natural language processing: Toward mitigating system bias and enabling better science. *Transactions of the Association for Computational Linguistics*, 6, 587-604. https://doi.org/10.1162/tacl_a_00041

[8] Sambasivan, N., Kapania, S., Highfill, H., Akrong, D., Paritosh, P., & Aroyo, L. M. (2021). "Everyone wants to do the model work, not the data work": Data cascades in high-stakes AI. *Proceedings of the 2021 CHI Conference on Human Factors in Computing Systems*, 1-15. https://doi.org/10.1145/3411764.3445518

[9] Hutchinson, B., Smart, A., Hber, A., Paullada, A., Denton, E., & Gebru, T. (2021). Towards accountability for machine learning datasets: Practices from software engineering and infrastructure. *Proceedings of the 2021 ACM Conference on Fairness, Accountability, and Transparency*, 560-575. https://doi.org/10.1145/3442188.3445918

[10] Bender, E. M., Gebru, T., McMillan-Major, A., & Shmitchell, S. (2021). On the dangers of stochastic parrots: Can language models be too big? *Proceedings of the 2021 ACM Conference on Fairness, Accountability, and Transparency*, 610-623. https://doi.org/10.1145/3442188.3445922

--- 

## Appendix A: Quick Validation Commands

```bash
# Schema check
alimentar schema /path/to/doctests.parquet

# Quality report
alimentar quality check /path/to/doctests.parquet

# Row count verification
alimentar info /path/to/doctests.parquet

# Sample inspection
alimentar head /path/to/doctests.parquet -n 20

# Checksum generation
sha256sum /path/to/doctests.parquet
```

## Appendix B: Prose Detection Verification (ALIM-R001)

```bash
# Run prose detection example to verify Poka-Yoke
cargo run --example prose_detection --features doctest

# Expected: All test cases pass
# - Prose sentences detected as prose (true)
# - Code outputs not detected as prose (false)
```

## Appendix C: Automated QA Integration

```yaml
# .github/workflows/dataset-qa.yml
name: Dataset QA
on: [push]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run QA Checks
        run: |
          alimentar quality check data/doctests.parquet
          alimentar schema data/doctests.parquet --validate
```
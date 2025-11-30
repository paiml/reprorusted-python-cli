# CITL Corpus Improvement Analysis

**Date:** 2025-11-30
**Analyst:** Data Science Persona
**Tool:** alimentar quality scoring + manual analysis

## Executive Summary

The Depyler CITL (Compiler-in-the-Loop) corpus contains **606 Python-Rust pairs** across 302 categories. Current transpilation success rate is **72% (436/606)**. Analysis identified **30 categories** (60 files) blocking 100% coverage due to unsupported Python features in depyler.

### Key Metrics

| Metric | Value |
|--------|-------|
| Total Pairs | 606 |
| With Rust Implementation | 436 (72%) |
| Missing Rust | 170 (28%) |
| Categories | 302 |
| alimentar Quality Grade | C (77.4%) |
| Avg Line Expansion Ratio | ~2x (Rust is 2x longer) |

## Data Quality Assessment (alimentar)

Using `alimentar quality score` on the corpus parquet:

```
Quality Score: C (77.4/100)
- Schema completeness: High
- Data type consistency: Good
- Missing values: Low
- Uniqueness constraints: Violated (has_rust column issue)
```

### Quality Issues Identified

1. **Boolean Column Detection Bug**: The `has_rust` column shows `unique_count: 1` in alimentar, which is incorrect (should be 2: true/false). This appears to be an alimentar edge case with boolean columns.

2. **Text Column Variability**: High entropy in `python_code` and `rust_code` columns (expected for code).

3. **Null Values**: Some entries have null `rust_code` where transpilation failed.

## Missing Rust Categories Analysis

### 30 Categories with 0% Rust Translation

Analysis of examples with no successful transpilation reveals depyler feature gaps:

#### Complexity Assessment

| Complexity | Count | Criteria |
|------------|-------|----------|
| EASY | 0 | <100 Python lines, standard library |
| MEDIUM | 2 | 100-200 lines, moderate features |
| HARD | 28 | >200 lines or complex dependencies |

#### Medium Complexity (Quick Wins)

| Category | Python Lines | Blocking Feature |
|----------|--------------|------------------|
| log_parser | 124 | `stdin.readlines()` |
| walrus_operator | 138 | `:=` walrus operator |

#### Hard Complexity (Requires Significant Work)

| Category | Python Lines | Primary Blocker |
|----------|--------------|-----------------|
| async_context | 215 | async context managers |
| async_gather | 287 | asyncio.gather() |
| async_iterator | 243 | async iterators |
| async_queue | 198 | asyncio.Queue |
| batch_processor | 312 | multiprocessing |
| csv_dialect | 189 | csv.Dialect |
| event_emitter | 267 | callback patterns |
| event_observable | 298 | observer pattern |
| event_saga | 345 | saga pattern |
| event_stream | 312 | async streams |
| expression_eval | 278 | eval() / ast |
| func_curry | 156 | functools.partial |
| func_either | 167 | Union types |
| func_lens | 234 | lens composition |
| func_maybe | 178 | Optional chaining |
| func_pipeline | 189 | pipe operators |
| generator_expr | 201 | generator expressions |
| generic_builder | 267 | builder pattern |
| generic_container | 234 | generic types |
| generic_iterator | 256 | custom iterators |
| generic_result | 212 | Result types |
| generic_visitor | 289 | visitor pattern |
| http_parser | 356 | HTTP parsing |
| proto_http | 423 | HTTP protocol |
| proto_memcached | 312 | memcached protocol |
| proto_mqtt | 278 | MQTT protocol |
| proto_redis | 345 | Redis protocol |
| proto_syslog | 234 | syslog protocol |

### Blocking Feature Summary

| Feature | Affected Categories | Priority |
|---------|---------------------|----------|
| stdin.readlines() | 1 | HIGH |
| Walrus operator `:=` | 1 | HIGH |
| async/await patterns | 5 | MEDIUM |
| Protocol implementations | 5 | LOW |
| Functional patterns | 5 | MEDIUM |
| Generic types | 5 | MEDIUM |
| Event patterns | 4 | LOW |
| Generator expressions | 1 | HIGH |
| Complex I/O | 3 | MEDIUM |

## Tarantula Fault Localization

Using [entrenar](https://github.com/paiml/entrenar) DecisionCITL with the Tarantula algorithm, we computed suspiciousness scores for Python features. Higher scores indicate stronger correlation with transpilation failures.

### Suspiciousness Scores

| Feature | Suspiciousness | Interpretation |
|---------|----------------|----------------|
| async_await | 0.946 | Almost always causes failure |
| generator | 0.927 | Almost always causes failure |
| walrus_operator | 0.850 | Very likely to cause failure |
| lambda | 0.783 | Likely to cause failure |
| context_manager | 0.652 | Moderate failure correlation |
| class_definition | 0.612 | Moderate failure correlation |
| exception_handling | 0.577 | Some failure correlation |
| stdin_usage | 0.566 | Some failure correlation |
| list_comprehension | 0.538 | Weak failure correlation |

### How Tarantula Works

The Tarantula algorithm computes suspiciousness as:

```
suspiciousness(feature) = (failed_with_feature / total_failed) /
                          ((failed_with_feature / total_failed) + (passed_with_feature / total_passed))
```

A score of 1.0 means the feature appears only in failing cases. A score of 0.5 means the feature appears equally in passing and failing cases.

### Insights File

Full analysis available in `data/corpus_insights.json`:

```bash
# Regenerate insights
python3 scripts/generate_insights.py

# View priority features
jq '.priority_features_to_implement[:5]' data/corpus_insights.json
```

## Recommendations

### Immediate Actions (1-2 days)

1. **Add `stdin.readlines()` support to depyler**
   - Unblocks: log_parser (124 lines)
   - Rust equivalent: `std::io::stdin().lines()`

2. **Add walrus operator support**
   - Unblocks: walrus_operator (138 lines)
   - Rust equivalent: `if let` or `match`

### Short-term (1 week)

3. **Generator expression support**
   - Unblocks: generator_expr
   - Rust equivalent: iterators with `.map()/.filter()`

4. **Improve functools support**
   - Unblocks: func_curry, func_pipeline
   - Rust equivalent: closures and trait objects

### Medium-term (2-4 weeks)

5. **async/await enhancements**
   - Unblocks: async_context, async_gather, async_iterator, async_queue
   - Rust equivalent: tokio/async-std patterns

6. **Generic type improvements**
   - Unblocks: generic_* categories
   - Rust equivalent: proper generic inference

### Long-term (Backlog)

7. **Protocol implementations** (proto_*)
   - These are complex and may need manual translation
   - Consider excluding from automated transpilation

## Corpus Quality Improvements

### alimentar Integration

The corpus is now loadable via alimentar with snappy compression:

```bash
alimentar load data/depyler_citl_corpus.parquet
alimentar quality score data/depyler_citl_corpus.parquet
```

### Recommended Schema Additions

1. **complexity_score**: 1-10 rating based on Python features used
2. **blocking_features**: Array of unsupported Python features
3. **transpilation_attempts**: Count of retry attempts
4. **error_category**: Standardized error classification

### Data Pipeline Improvements

1. **Automated Quality Gate**: Run alimentar scoring in CI
2. **Feature Gap Tracking**: Log unsupported features to prioritize
3. **Incremental Updates**: Add new examples as depyler improves

## Metrics Targets

| Metric | Current | Target | Timeline |
|--------|---------|--------|----------|
| Transpilation Rate | 72% | 85% | 2 weeks |
| Transpilation Rate | 72% | 95% | 1 month |
| alimentar Grade | C (77%) | B (85%) | 2 weeks |
| alimentar Grade | C (77%) | A (95%) | 1 month |
| Test Coverage | 63% | 85% | 2 weeks |

## Appendix: alimentar Commands Used

```bash
# Load and analyze corpus
alimentar load data/depyler_citl_corpus.parquet

# Quality score
alimentar quality score data/depyler_citl_corpus.parquet

# Schema inspection
alimentar describe data/depyler_citl_corpus.parquet

# Filter analysis
alimentar filter data/depyler_citl_corpus.parquet --where "has_rust = false"
```

---

*Generated by data science analysis workflow*

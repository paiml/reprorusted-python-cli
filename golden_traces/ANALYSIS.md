# Golden Trace Analysis Report

## Overview

This directory contains golden traces captured from reprorusted-python-cli examples.

## Trace Files

| File | Description | Format |
|------|-------------|--------|
| `trivial_cli_rust.json` | Full syscall trace (Rust) | JSON |
| `trivial_cli_rust_summary.txt` | Statistical summary (Rust) | Text |
| `trivial_cli_rust_source.json` | Trace with source locations | JSON |

## How to Use These Traces

### 1. Regression Testing

Compare new builds against golden traces:

```bash
# Capture new trace
renacer --format json -- ./new_build > new_trace.json

# Compare with golden (manual diff)
diff trivial_cli_rust.json new_trace.json

# Or use semantic equivalence validator (in test suite)
cargo test --test semantic_equivalence
```

### 2. Performance Budgeting

Check if new build meets performance requirements:

```bash
# Run with assertions
cargo test --test performance_assertions

# Or manually check against summary
cat trivial_cli_rust_summary.txt
```

### 3. CI/CD Integration

Add to `.github/workflows/ci.yml`:

```yaml
- name: Validate Performance
  run: |
    renacer --format json -- ./target/release/cli > trace.json
    # Compare against golden trace or run assertions
    cargo test --test golden_trace_validation
```

## Trace Interpretation Guide

### JSON Trace Format

```json
{
  "version": "0.6.2",
  "format": "renacer-json-v1",
  "syscalls": [
    {
      "name": "write",
      "args": ["1", "Hello, GoldenTest!\n", "19"],
      "result": 19
    }
  ]
}
```

### Summary Statistics Format

```
% time     seconds  usecs/call     calls    errors syscall
------ ----------- ----------- --------- --------- ----------------
 19.27    0.000137          10        13           mmap
 14.35    0.000102          17         6           write
...
```

**Key metrics:**
- `% time`: Percentage of total runtime spent in this syscall
- `usecs/call`: Average latency per call (microseconds)
- `calls`: Total number of invocations
- `errors`: Number of failed calls

## Next Steps

1. **Set performance baselines** using these golden traces
2. **Add assertions** in `renacer.toml` for automated checking
3. **Integrate with CI** to prevent regressions
4. **Compare Python vs Rust** traces for semantic equivalence

Generated: $(date)

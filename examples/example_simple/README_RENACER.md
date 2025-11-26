# Renacer Integration for trivial_cli

This directory demonstrates **golden trace validation** using Renacer for the `trivial_cli` example.

## Quick Start

### 1. Capture Golden Traces

```bash
# From project root
./scripts/capture_golden_traces.sh
```

This creates:
- `golden_traces/trivial_cli_rust.json` - Full syscall trace
- `golden_traces/trivial_cli_rust_summary.txt` - Statistical summary
- `golden_traces/trivial_cli_rust_source.json` - Trace with source locations

### 2. Run Validation Tests

```bash
cd examples/example_simple
cargo test --test golden_trace_validation
```

### 3. View Traces

```bash
# Summary statistics
cat ../../golden_traces/trivial_cli_rust_summary.txt

# Full JSON trace (formatted)
jq . ../../golden_traces/trivial_cli_rust.json | less

# Syscall timeline
renacer --timing -- ./trivial_cli --name "Test"
```

## Test Suite

### Automated Tests (cargo test)

| Test | Purpose |
|------|---------|
| `test_cli_execution_completes` | Smoke test - CLI executes |
| `test_golden_trace_exists` | Verify golden trace captured |
| `test_golden_trace_format` | Validate JSON structure |
| `test_performance_baseline` | Check runtime <2ms |
| `test_syscall_count_budget` | Check syscalls <100 |
| `test_expected_syscall_patterns` | Verify write/alloc syscalls |

### Manual Regression Test

```bash
# Run regression check (compares against golden)
cargo test --test golden_trace_validation test_regression_check -- --ignored
```

## Performance Baselines

From golden trace capture:

| Metric | Value | Budget |
|--------|-------|--------|
| Total Runtime | 0.561ms | <2ms ✅ |
| Total Syscalls | 65 | <100 ✅ |
| Write Operations | 1 | Expected ✅ |
| Memory Allocations | 13 mmap + 3 brk | Normal ✅ |

## CI/CD Integration

Add to `.github/workflows/ci.yml`:

```yaml
name: Golden Trace Validation

on: [push, pull_request]

jobs:
  validate-traces:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install Renacer
        run: cargo install renacer

      - name: Build Examples
        run: cargo build --release --examples

      - name: Capture Golden Traces
        run: ./scripts/capture_golden_traces.sh

      - name: Run Validation Tests
        run: |
          cd examples/example_simple
          cargo test --test golden_trace_validation

      - name: Upload Traces (Artifact)
        uses: actions/upload-artifact@v3
        with:
          name: golden-traces
          path: golden_traces/
```

## Troubleshooting

### Test fails: "Golden trace should exist"

**Solution:**
```bash
./scripts/capture_golden_traces.sh
```

### Test fails: Performance regression

**Diagnosis:**
```bash
# Compare current vs golden
renacer --summary --timing -- ./trivial_cli --name "Test"
cat ../../golden_traces/trivial_cli_rust_summary.txt
```

**Common causes:**
- Debug build (use `--release`)
- CI environment variance (increase tolerance)
- New dependencies added

### Test fails: Syscall count regression

**Diagnosis:**
```bash
# Detailed syscall comparison
renacer -- ./trivial_cli --name "Test" > current_trace.txt
diff current_trace.txt ../../golden_traces/trivial_cli_rust.txt
```

**Common causes:**
- New library initialization
- Environment differences (locale, TZ, etc.)
- Tracing overhead variance

## Advanced Usage

### Compare Python vs Rust

```bash
# Trace Python version (if available)
renacer --format json -- python trivial_cli.py --name "Test" > python_trace.json

# Compare
diff python_trace.json ../../golden_traces/trivial_cli_rust.json
```

### Source Code Correlation

```bash
# Rebuild with debug symbols
RUSTFLAGS="-C debuginfo=2" cargo build --release

# Trace with source locations
renacer -s -- ./trivial_cli --name "Test"
```

Output:
```
write(1, "Hello, Test!\n", 13) = 13  [src/main.rs:42]
```

### Export to OpenTelemetry

```bash
# Start OTLP collector (Jaeger/Tempo)
docker run -d -p 4317:4317 otel/opentelemetry-collector

# Export trace
renacer --otlp http://localhost:4317 -- ./trivial_cli --name "Test"

# View in Jaeger UI
open http://localhost:16686
```

## Renacer Features Used

✅ **JSON Export** - Machine-readable trace format
✅ **Summary Statistics** - Performance baselines
✅ **Source Correlation** - Map syscalls to Rust code
✅ **Low Overhead** - <1% runtime impact
✅ **Golden Traces** - Regression detection

## Next Steps

1. **Add more examples** - Capture traces for all CLI examples
2. **Implement semantic equivalence** - Compare Python vs Rust traces
3. **Add performance assertions** - Define budgets in `renacer.toml`
4. **Integrate with CI** - Automated golden trace validation
5. **Monitor production** - Export traces to observability stack

## References

- [Renacer Documentation](https://github.com/paiml/renacer)
- [Golden Trace Integration Report](../../docs/integration-report-golden-trace.md)
- [OpenTelemetry Specification](https://opentelemetry.io/docs/specs/otel/)

---

**Generated:** $(date)
**Renacer Version:** 0.6.2

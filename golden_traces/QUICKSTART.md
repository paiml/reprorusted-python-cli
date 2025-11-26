# Golden Trace Validation: Quick Start Guide

**Goal**: Validate semantic equivalence between Python and Rust transpilations using Renacer

**Time**: ~5 minutes per example

**Prerequisites**:
- Renacer v0.6.2 installed (`cargo install renacer` or use system binary)
- Rust example compiles successfully (`cargo build --release`)
- Python example runs successfully

---

## 4-Step Validation Workflow

### Step 1: Capture Python Golden Trace

```bash
cd examples/YOUR_EXAMPLE

# Run with renacer to capture syscall trace
renacer --format json -- python3 YOUR_SCRIPT.py [ARGS] \
  > ../../golden_traces/python/YOUR_EXAMPLE_golden.json 2>&1

# Verify trace was captured
ls -lh ../../golden_traces/python/YOUR_EXAMPLE_golden.json
```

**Expected**: JSON file ~150-200 KB with ~1,200 syscalls

### Step 2: Build Rust Binary

```bash
# Build release binary
cargo build --release

# Verify it runs
./target/release/YOUR_BINARY [ARGS]
```

**Expected**: Same output as Python version (exact or semantically equivalent)

### Step 3: Capture Rust Golden Trace

```bash
# Run Rust binary with renacer
renacer --format json -- ./target/release/YOUR_BINARY [ARGS] \
  > ../../golden_traces/rust/YOUR_EXAMPLE_golden.json 2>&1

# Verify trace was captured
ls -lh ../../golden_traces/rust/YOUR_EXAMPLE_golden.json
```

**Expected**: JSON file ~9-10 KB with ~65-70 syscalls

### Step 4: Validate Equivalence

```bash
# Count syscalls
cd ../../golden_traces

# Python syscalls
grep '"name":' python/YOUR_EXAMPLE_golden.json | wc -l

# Rust syscalls
grep '"name":' rust/YOUR_EXAMPLE_golden.json | wc -l

# Calculate improvement
echo "scale=1; PYTHON_COUNT / RUST_COUNT" | bc

# Compare outputs
diff <(python3 ../examples/YOUR_EXAMPLE/YOUR_SCRIPT.py [ARGS]) \
     <(../examples/YOUR_EXAMPLE/target/release/YOUR_BINARY [ARGS])
```

**Expected**:
- Python: ~1,200 syscalls
- Rust: ~65-70 syscalls
- Improvement: ~17-19×
- Output: Identical or semantically equivalent

---

## Complete Example

### Example: trivial_cli

```bash
# Step 1: Python trace
cd /home/noah/src/reprorusted-python-cli/examples/example_simple
renacer --format json -- python3 trivial_cli.py --name "Test" \
  > ../../golden_traces/python/trivial_cli_golden.json 2>&1

# Step 2: Build Rust
cargo build --release

# Step 3: Rust trace
renacer --format json -- ./target/release/trivial_cli --name "Test" \
  > ../../golden_traces/rust/trivial_cli_golden.json 2>&1

# Step 4: Validate
cd ../../golden_traces
echo "Python syscalls: $(grep '"name":' python/trivial_cli_golden.json | wc -l)"
echo "Rust syscalls: $(grep '"name":' rust/trivial_cli_golden.json | wc -l)"
echo "Improvement: $(echo "scale=1; 1220 / 65" | bc)x"

# Compare outputs
diff <(python3 ../examples/example_simple/trivial_cli.py --name "Test") \
     <(../examples/example_simple/target/release/trivial_cli --name "Test")
```

**Result**:
```
Python syscalls: 1220
Rust syscalls: 65
Improvement: 18.7x
Output: ✅ IDENTICAL
```

---

## Automated Summary

Generate summary table for all validated examples:

```bash
cd /home/noah/src/reprorusted-python-cli
./scripts/generate_golden_summary.sh
```

**Output**:
```markdown
| Example | Python Syscalls | Rust Syscalls | Improvement | Python Size | Rust Size |
|---------|----------------|---------------|-------------|-------------|-----------|
| trivial_cli | 1220 | 65 | **18.7×** | 193K | 9.4K |
| git_clone | 1266 | 65 | **19.4×** | 200K | 9.4K |
...
```

---

## Common Issues

### Issue: Empty or corrupted trace file

**Symptom**: Trace file is 0 bytes or missing JSON

**Solution**:
1. Check stderr output: `renacer ... 2>&1 | tee trace.log`
2. Verify renacer is installed: `which renacer`
3. Check permissions on output directory

### Issue: Syscall count is 0

**Symptom**: `grep '"name":' trace.json | wc -l` returns 0

**Solution**:
1. Check trace file format: `head -20 trace.json`
2. Verify JSON is valid: `jq . trace.json`
3. Look for output mixed with trace: Output should be on first line, JSON starts line 2

### Issue: Output differs between Python and Rust

**Symptom**: `diff` shows differences

**Expected Differences** (semantically equivalent):
- Boolean: `True` vs `true`
- Quotes: `['item']` vs `["item"]`
- Debug format: `value` vs `"value"`

**Unexpected Differences** (semantic divergence):
- Different values
- Missing fields
- Extra output
- ❌ **This is a transpiler bug - STOP THE LINE!**

---

## Performance Expectations

### Typical Results

| Metric | Python | Rust | Improvement |
|--------|--------|------|-------------|
| Syscalls | 1,200-1,300 | 65-70 | **17-19×** |
| Trace size | 190-200 KB | 9-10 KB | **20×** |
| Variance | ±20 calls (1.5%) | ±2 calls (3%) | Low variance |

### Red Flags

⚠️ **Alert if**:
- Rust syscalls > 100 (should be ~65-70)
- Improvement < 10× (should be ~18×)
- Output differs unexpectedly
- Variance > 10% (should be <5%)

---

## Integration with CI/CD

### GitHub Actions Example

Add to `.github/workflows/ci.yml`:

```yaml
- name: Golden Trace Validation
  run: |
    cargo install renacer

    for example in trivial_cli git_clone flag_parser positional_args complex_cli; do
      cd examples/example_${example}

      # Capture Python trace
      renacer --format json -- python3 ${example}.py [ARGS] \
        > ../../golden_traces/python/${example}_ci.json

      # Build and capture Rust trace
      cargo build --release
      renacer --format json -- ./target/release/${example} [ARGS] \
        > ../../golden_traces/rust/${example}_ci.json

      # Validate (fail on divergence)
      diff <(python3 ${example}.py [ARGS]) \
           <(./target/release/${example} [ARGS]) || exit 1

      cd ../..
    done
```

### Performance Regression Check

```yaml
- name: Check Performance Regression
  run: |
    PYTHON_COUNT=$(grep '"name":' golden_traces/python/example_ci.json | wc -l)
    RUST_COUNT=$(grep '"name":' golden_traces/rust/example_ci.json | wc -l)

    # Fail if Rust > 150 syscalls (budgeted limit)
    if [ $RUST_COUNT -gt 150 ]; then
      echo "❌ Performance regression: $RUST_COUNT syscalls (limit: 150)"
      exit 1
    fi

    # Fail if improvement < 3×
    IMPROVEMENT=$(echo "scale=1; $PYTHON_COUNT / $RUST_COUNT" | bc)
    if [ $(echo "$IMPROVEMENT < 3.0" | bc) -eq 1 ]; then
      echo "❌ Performance regression: ${IMPROVEMENT}× (minimum: 3×)"
      exit 1
    fi

    echo "✅ Performance: ${IMPROVEMENT}× improvement ($RUST_COUNT syscalls)"
```

---

## Tips and Best Practices

### 1. Use Consistent Arguments

**Always use the same arguments** for Python and Rust traces:
```bash
# Good
ARGS="--name Test --verbose"
renacer --format json -- python3 script.py $ARGS > python.json
renacer --format json -- ./binary $ARGS > rust.json

# Bad (different args)
renacer --format json -- python3 script.py --name A > python.json
renacer --format json -- ./binary --name B > rust.json
```

### 2. Clean Output First

If your script prints to stdout before parsing args:
```bash
# Output will be on first line of trace
head -1 rust_trace.json  # Shows actual output
tail -n +2 rust_trace.json | jq .  # Shows JSON trace
```

### 3. Check File Sizes

Quick sanity check:
```bash
# Python trace should be ~190-200 KB
# Rust trace should be ~9-10 KB
ls -lh golden_traces/python/*.json
ls -lh golden_traces/rust/*.json
```

### 4. Document Semantic Differences

If output differs but is semantically equivalent:
```markdown
**Semantic Equivalence Note**:
- Python outputs: `Verbose: True`
- Rust outputs: `Verbose: true`
- **Validation**: ✅ PASS - Boolean representation difference
```

---

## Troubleshooting

### Renacer not found

```bash
# Install renacer
cargo install renacer

# Or use system binary
export PATH=$PATH:/home/noah/src/renacer/target/debug
```

### Trace is too large

```bash
# Enable compression in renacer.toml
[compression]
enabled = true
algorithm = "rle"  # 10× size reduction
```

### Output mixed with trace

**Problem**: Output appears in JSON trace

**Solution**: Renacer puts output on first line, JSON starts line 2:
```bash
# Extract output
head -1 trace.json

# Extract JSON
tail -n +2 trace.json | jq .
```

---

## Reference Documentation

- **MULTI-EXAMPLE-SUMMARY.md**: Aggregate analysis of all examples
- **VALIDATION-REPORT.md**: Detailed single-example report
- **FINAL-SUMMARY.md**: Complete validation summary
- **Renacer Integration Report**: `docs/integration-report-golden-trace.md`

---

## Quick Commands Reference

```bash
# Capture Python trace
renacer --format json -- python3 script.py [ARGS] > python.json 2>&1

# Capture Rust trace
renacer --format json -- ./binary [ARGS] > rust.json 2>&1

# Count syscalls
grep '"name":' trace.json | wc -l

# Compare output
diff <(python3 script.py [ARGS]) <(./binary [ARGS])

# Generate summary
./scripts/generate_golden_summary.sh

# Validate all traces
for f in golden_traces/python/*.json; do
  echo "$f: $(grep '"name":' "$f" | wc -l) syscalls"
done
```

---

**Last Updated**: 2025-11-23
**Renacer Version**: 0.6.2
**Validated Examples**: 5/5 (100%)
**Average Improvement**: 18.4×

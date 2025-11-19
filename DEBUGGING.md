# Debugging Guide - Depyler Transpilation & Runtime Analysis

**Complete workflow for debugging Python-to-Rust transpilation issues with reproducibility**

This guide covers five critical debugging phases:
1. **Transpilation Debugging** - Using `depyler --trace` and `--explain`
2. **Compile-Time Analysis** - Understanding Rust compiler errors
3. **Runtime Tracing** - Using `renacer` for syscall and function profiling
4. **Transpiler Source Mapping** - Using `renacer --transpiler-map` for Python→Rust correlation (v0.4.1+)
5. **Chaos Engineering** - Stress testing transpiled code with chaos infrastructure (v0.4.1+)

---

## 🔍 Phase 1: Transpilation Debugging

### Quick Reference

```bash
# Show transpilation phases (AST → HIR → Rust)
depyler transpile example.py --trace

# Explain transformation decisions
depyler transpile example.py --explain

# Combined for maximum detail
depyler transpile example.py --trace --explain > debug_output.txt
```

### When to Use Each Flag

| Flag | Purpose | Output Size | Use Case |
|------|---------|-------------|----------|
| `--trace` | Show AST → HIR → Rust phases | Medium | Understanding transformation flow |
| `--explain` | Explain decision rationale | Large | Investigating unexpected transformations |
| Both | Complete analysis | Very Large | Bug reports and reproducibility |

---

### Example 1: Debugging Variable Scope Issues

**Problem**: Variables not accessible in if/else blocks

```bash
# Python code with scope issue
cat > scope_test.py << 'EOF'
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['dev', 'prod'])
    args = parser.parse_args()

    if args.mode == 'dev':
        env = 'development'
    else:
        env = 'production'

    print(f"Environment: {env}")

if __name__ == "__main__":
    main()
EOF

# Debug with trace
depyler transpile scope_test.py --trace

# Look for:
# ✅ Variable hoisting patterns
# ✅ Scope boundaries in HIR
# ❌ Missing variable declarations
```

**Expected Output** (with --trace):
```
[PHASE 1] Python AST Parse
  - Found function: main
  - Found if/else statement
  - Variable 'env' assigned in both branches

[PHASE 2] HIR Generation
  - Hoisting 'env' declaration to function scope
  - Mapping if/else to Rust match or if/else

[PHASE 3] Rust Code Generation
  - Generated: let mut env: String;
  - Generated: if args.mode == "dev" { env = "development".to_string(); }
```

---

### Example 2: Debugging Type Inference

**Problem**: Type mismatches in generated Rust code

```bash
# Python code with type inference challenge
cat > type_test.py << 'EOF'
import argparse

def process_items(items):
    """Process list of items"""
    count = len(items)
    result = items[0] if count > 0 else "none"
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('items', nargs='+')
    args = parser.parse_args()

    output = process_items(args.items)
    print(output)

if __name__ == "__main__":
    main()
EOF

# Debug with explain
depyler transpile type_test.py --explain

# Look for:
# ✅ Type inference decisions for 'result'
# ✅ List vs String type resolution
# ❌ Conflicting type constraints
```

**Expected Output** (with --explain):
```
[TYPE INFERENCE] Variable 'result'
  - Branch 1: items[0] → String (from Vec<String> indexing)
  - Branch 2: "none" → &str literal
  - Resolution: Unified to String
  - Decision: Convert &str to String for consistency
  - Generated: let result: String = if count > 0 { items[0].clone() } else { "none".to_string() };
```

---

### Example 3: Debugging argparse Transformations

**Problem**: Understanding how argparse maps to clap

```bash
# Python argparse with multiple patterns
cat > argparse_test.py << 'EOF'
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Test argparse patterns",
        prog="test_cli"
    )

    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--count', type=int, default=1)
    parser.add_argument('files', nargs='+', help='Files to process')

    args = parser.parse_args()
    print(f"Verbose: {args.verbose}, Count: {args.count}")
    print(f"Files: {args.files}")

if __name__ == "__main__":
    main()
EOF

# Debug with trace + explain
depyler transpile argparse_test.py --trace --explain > argparse_debug.txt

# Analyze the output
grep -A5 "ArgumentParser" argparse_debug.txt
grep -A5 "add_argument" argparse_debug.txt
grep -A5 "clap" argparse_debug.txt
```

**Key Patterns to Look For**:
```
[EXPLAIN] ArgumentParser()
  - description → #[command(about = "Test argparse patterns")]
  - prog → #[command(name = "test_cli")]

[EXPLAIN] add_argument('--verbose', action='store_true')
  - Mapping: action='store_true' → bool field with #[arg(short, long)]
  - Generated: #[arg(long)] pub verbose: bool

[EXPLAIN] add_argument('files', nargs='+')
  - Mapping: positional + nargs='+' → Vec<String>
  - Generated: #[arg(required = true)] pub files: Vec<String>
```

---

## 🛠️ Phase 2: Compile-Time Analysis

### Systematic Debugging Workflow

```bash
# Step 1: Transpile with dependency generation
depyler transpile example.py --trace --explain > transpile.log

# Step 2: Setup Rust project structure
mkdir -p /tmp/debug_project/src
depyler transpile example.py -o /tmp/debug_project/src/main.rs

# Step 3: Attempt build with detailed errors
cd /tmp/debug_project
cargo build 2>&1 | tee build_errors.txt

# Step 4: Analyze error categories
grep "error\[E" build_errors.txt | sort | uniq -c
```

### Common Error Categories

#### Error E0277: Trait Bound Not Satisfied

```bash
# Example error
error[E0277]: the trait `std::fmt::Display` is not implemented for `Vec<String>`
   --> src/main.rs:42:20
    |
42  |     println!("{}", args.files);
    |                    ^^^^^^^^^^ `Vec<String>` cannot be formatted with the default formatter

# Root Cause Analysis
# 1. Check transpilation output
depyler transpile example.py --trace | grep -A3 "println"

# 2. Look for:
#    - println!("{}", Vec<T>) patterns
#    - Should use Debug trait: println!("{:?}", ...)
#    - Or join: println!("{}", vec.join(", "))
```

#### Error E0433: Unresolved Import

```bash
# Example error
error[E0433]: failed to resolve: use of unresolved crate `serde_json`
   --> src/main.rs:15:24
    |
15  | pub fn process(data: serde_json::Value) {
    |                      ^^^^^^^^^^^ use of undeclared crate or module

# Root Cause Analysis
# 1. Check Cargo.toml for missing dependency
cat Cargo.toml | grep serde_json

# 2. Check if type annotation triggered import
depyler transpile example.py --explain | grep -A5 "Type annotation"

# 3. Verify dependency detection
depyler transpile example.py --trace | grep "dependencies detected"
```

#### Error E0609: No Field on Type

```bash
# Example error
error[E0609]: no field `repository` on type `&Args`
   --> src/main.rs:28:18
    |
28  |     println!("{}", args.repository);
    |                    ^^^^^^^^^^^^^^^ unknown field

# Root Cause Analysis
# 1. Check struct definition
depyler transpile example.py --trace | grep -A10 "struct Args"

# 2. Look for field definition
depyler transpile example.py --explain | grep "repository"

# 3. Verify argparse mapping
grep -A5 "add_argument.*repository" example.py
```

---

## 🔬 Phase 3: Runtime Tracing with Renacer

### Overview

**Renacer** is a pure Rust syscall tracer with source-level correlation. Use it to:
- Trace syscalls (read, write, open, etc.)
- Profile function execution time
- Detect I/O bottlenecks
- Generate flamegraphs
- Debug runtime behavior

### Installation

```bash
# Install from source
cd ../renacer
cargo install --path .

# Verify installation
renacer --version
```

---

### Example 1: Basic Syscall Tracing

```bash
# Build a working example
cd examples/example_simple
depyler compile trivial_cli.py -o trivial_cli

# Trace syscalls
renacer -- ./trivial_cli --name "Test"

# Expected output:
# openat(AT_FDCWD, "/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 3
# write(1, "Hello, Test!\n", 13) = 13
# exit_group(0) = ?
```

**Analysis**:
- ✅ Verify correct syscalls are made
- ✅ Check for unexpected file operations
- ✅ Validate argument passing

---

### Example 2: Source-Level Correlation

```bash
# Compile with debug symbols
cd examples/example_flags
cargo build  # Debug build includes symbols

# Trace with source correlation
renacer --source -- ./target/debug/flag_parser --verbose --debug

# Expected output:
# write(1, "Verbose: true\n", 14) = 14    [src/main.rs:42 in main]
# write(1, "Debug: true\n", 12) = 12      [src/main.rs:43 in main]

# Analysis: Correlate Rust source lines with syscalls
```

**Use Cases**:
- **Bug localization**: Find exact source line causing syscall issues
- **Performance analysis**: Identify which functions make slow syscalls
- **Security audit**: Verify sensitive operations happen in correct code paths

---

### Example 3: Function Profiling & Flamegraphs

```bash
# Build complex example with debug symbols
cd examples/example_regex
cargo build --release  # Can still profile release builds

# Profile function execution time
renacer --function-time --source -- ./target/release/regex_tool search "pattern" test.txt

# Expected output:
# Function Profiling Summary:
# ========================
# Total functions profiled: 8
# Total syscalls: 42
#
# Top 10 Hot Paths (by total time):
#   1. regex_tool::search_file  - 65.2% (850ms, 28 syscalls) ⚠️ SLOW I/O
#   2. std::io::BufReader::read - 22.1% (288ms, 12 syscalls)
#   3. regex::compile           - 8.5% (111ms, 2 syscalls)

# Generate flamegraph
renacer --function-time --source -- ./target/release/regex_tool search "pattern" test.txt > profile.txt
cat profile.txt | flamegraph.pl > flamegraph.svg
```

**Optimization Workflow**:
1. Identify hot paths with `--function-time`
2. Locate bottlenecks marked with ⚠️ SLOW I/O
3. Review source code at identified locations
4. Refactor and re-profile

---

### Example 4: I/O Bottleneck Detection

```bash
# Profile I/O-heavy example
cd examples/example_io_streams
cargo build

# Detect slow I/O operations
renacer --function-time --source -- ./target/debug/stream_processor read large_file.txt

# Look for ⚠️ SLOW I/O markers (operations >1ms)
# Example output:
#   1. stream_processor::read_file - 82.5% (2.1s, 156 syscalls) ⚠️ SLOW I/O
#   2. std::fs::File::read         - 75.2% (1.9s, 145 syscalls) ⚠️ SLOW I/O

# Investigate with syscall filtering
renacer -e trace=file -- ./target/debug/stream_processor read large_file.txt

# Show only file operations:
# openat(AT_FDCWD, "large_file.txt", O_RDONLY) = 3
# read(3, buf, 8192) = 8192  [145 times, total 2.1s]
```

**Root Cause Analysis**:
- Small buffer sizes (8192 bytes) causing excessive syscalls
- **Fix**: Increase buffer size to reduce syscall overhead

---

## 📊 Complete Debugging Example - End-to-End

### Scenario: Debugging example_positional Build Failure

**Problem**: Vec<String> Display trait error

#### Step 1: Transpilation Analysis

```bash
cd examples/example_positional

# Generate trace
depyler transpile positional_args.py --trace --explain > debug.log

# Find println! usage
grep -A5 "println!" debug.log

# Output shows:
# [CODE GEN] println! macro
#   - Template: println!("{}", args.targets)
#   - Type: Vec<String>
#   - Issue: Vec<String> doesn't implement Display trait ❌
```

**Finding**: Generated code tries to print Vec<String> directly

---

#### Step 2: Verify Build Error

```bash
# Setup project
mkdir -p /tmp/positional_test/src
depyler transpile positional_args.py -o /tmp/positional_test/src/main.rs

# Build and capture error
cd /tmp/positional_test
cargo build 2>&1 | tee build.log

# Analyze error
cat build.log

# Output:
# error[E0277]: the trait `std::fmt::Display` is not implemented for `Vec<String>`
#   --> src/main.rs:42:20
#    |
# 42 |     println!("{}", args.targets);
#    |                    ^^^^^^^^^^^^
```

**Confirmation**: Build error matches transpilation analysis ✅

---

#### Step 3: Manual Fix & Validation

```bash
# Fix: Use Debug trait instead
sed -i 's/println!("{}", args.targets)/println!("{:?}", args.targets)/' src/main.rs

# Rebuild
cargo build --release

# Success! ✅
# Output: Finished `release` profile [optimized] target(s) in 2.43s

# Test runtime behavior
./target/release/positional_args file1.txt file2.txt file3.txt

# Output: Targets: ["file1.txt", "file2.txt", "file3.txt"]
```

---

#### Step 4: Runtime Verification with Renacer

```bash
# Trace syscalls to verify correct behavior
renacer -- ./target/release/positional_args file1.txt file2.txt

# Expected syscalls:
# write(1, "Targets: [\"file1.txt\", \"file2.txt\"]\n", 37) = 37 ✅

# With source correlation
renacer --source -- ./target/release/positional_args file1.txt

# Output:
# write(1, "Targets: ...", 37) = 37  [src/main.rs:42 in main] ✅
```

**Validation**: Runtime behavior matches expectations ✅

---

#### Step 5: Document for Reproducibility

```bash
# Create reproducible bug report
cat > BUG_REPORT.md << 'EOF'
# Bug Report: Vec<String> Display Trait

## Reproduction

```bash
# 1. Transpile with trace
depyler transpile positional_args.py --trace --explain > trace.log

# 2. Setup project
mkdir -p /tmp/test/src
depyler transpile positional_args.py -o /tmp/test/src/main.rs

# 3. Attempt build (FAILS)
cd /tmp/test
cargo build 2>&1 | tee error.log
```

## Expected Error

```
error[E0277]: the trait `std::fmt::Display` is not implemented for `Vec<String>`
```

## Root Cause

Transpilation generates:
```rust
println!("{}", args.targets);  // Vec<String> ❌
```

Should generate:
```rust
println!("{:?}", args.targets);  // Debug trait ✅
```

## Fix

Detect Vec<T> in println! patterns and use Debug trait.

## Validation

After fix, verify with renacer:
```bash
renacer --source -- ./binary arg1 arg2
# Should show write syscall with correct formatting
```
EOF

cat BUG_REPORT.md
```

**Result**: Complete reproducible bug report for depyler issue tracker ✅

---

## 🎯 Debugging Cheatsheet

### Quick Commands

```bash
# Transpilation debugging
depyler transpile example.py --trace                    # Show phases
depyler transpile example.py --explain                  # Explain decisions
depyler transpile example.py --trace --explain > out.txt  # Full analysis

# Build debugging
cargo build 2>&1 | tee build.log                        # Capture errors
grep "error\[E" build.log | sort | uniq -c               # Count error types
cargo build --verbose                                   # Detailed build output

# Runtime tracing
renacer -- ./binary args                                # Basic syscall trace
renacer --source -- ./binary                            # With source correlation
renacer --function-time --source -- ./binary            # Function profiling
renacer -e trace=file -- ./binary                       # Filter file operations
renacer -c -T -- ./binary                               # Statistics + timing

# Flamegraph generation
renacer --function-time --source -- ./binary > profile.txt
cat profile.txt | flamegraph.pl > flamegraph.svg
```

### Error Investigation Workflow

1. **Transpilation Phase**
   ```bash
   depyler transpile example.py --trace --explain > trace.log
   # Check trace.log for transformation issues
   ```

2. **Build Phase**
   ```bash
   cargo build 2>&1 | tee build.log
   grep "error\[E" build.log | head -1
   # Identify primary error type
   ```

3. **Root Cause Analysis**
   ```bash
   # Cross-reference transpile trace with build error
   grep -A10 "error_line_content" trace.log
   ```

4. **Runtime Validation**
   ```bash
   renacer --source -- ./binary
   # Verify behavior matches expectations
   ```

---

## 📚 Additional Resources

### Depyler Resources
- **Documentation**: [../depyler/README.md](../depyler/README.md)
- **Issue Tracker**: https://github.com/paiml/reprorusted-python-cli/issues
- **Compatibility Matrix**: [STATUS.md](STATUS.md)

### Renacer Resources
- **Documentation**: [../renacer/README.md](../renacer/README.md)
- **Specification**: [../renacer/docs/specifications/deep-strace-rust-wasm-binary-spec.md](../renacer/docs/specifications/deep-strace-rust-wasm-binary-spec.md)
- **Examples**: [../renacer/tests/](../renacer/tests/)

### Rust Resources
- **Rust Errors Index**: https://doc.rust-lang.org/error-index.html
- **Clippy Lints**: https://rust-lang.github.io/rust-clippy/master/
- **Cargo Book**: https://doc.rust-lang.org/cargo/

---

## 🏆 Best Practices

### 1. Always Use --trace --explain for Bug Reports

**Bad** ❌:
```
depyler transpile example.py
# Error during transpilation
```

**Good** ✅:
```bash
depyler transpile example.py --trace --explain > debug.log
# Include debug.log in bug report with exact error location
```

### 2. Verify Runtime Behavior with Renacer

**Bad** ❌:
```bash
cargo build && ./binary arg1 arg2
# Assume it works correctly
```

**Good** ✅:
```bash
cargo build && renacer --source -- ./binary arg1 arg2
# Verify syscalls and source correlation
```

### 3. Create Minimal Reproducible Examples

**Bad** ❌:
```python
# 500-line production script with complex dependencies
```

**Good** ✅:
```python
# Minimal 20-line script isolating the specific issue
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('items', nargs='+')
    args = parser.parse_args()
    print(args.items)  # Issue: Vec<String> Display

if __name__ == "__main__":
    main()
```

### 4. Document Debugging Session

Create `DEBUGGING_SESSION.md`:
```markdown
# Debugging Session: 2025-11-17

## Issue
Vec<String> Display trait not implemented

## Commands Run
1. `depyler transpile example.py --trace > trace.log`
2. `cargo build 2>&1 | tee build.log`
3. Fixed manually: `s/println!("{}", /println!("{:?}", /`
4. `renacer --source -- ./binary` (verified ✅)

## Root Cause
Line 42: println!("{}", args.targets) should use Debug trait

## Fix Needed
Detect Vec<T> in println! and auto-generate Debug trait usage
```

---

### Example 4: Transpiler Source Mapping (Renacer v0.4.1+)

**NEW in Sprint 24**: Correlate transpiled Rust code back to original Python source

#### Overview

Renacer v0.4.1 introduces `--transpiler-map` for mapping generated Rust code back to original Python source. This enables:
- **Python→Rust line correlation** - Map Rust errors to Python source
- **Python function names** - Preserve original function names in profiles
- **Error context** - Understand which Python code caused Rust compile errors

#### Source Map Format

Depyler (future version) will generate `.sourcemap.json` files alongside `.rs` files:

```json
{
  "version": 1,
  "source_language": "python",
  "source_file": "examples/csv_filter.py",
  "generated_file": "csv_filter.rs",
  "depyler_version": "3.20.0+50",

  "mappings": [
    {
      "rust_line": 52,
      "rust_function": "filter_csv",
      "python_line": 28,
      "python_function": "filter_csv",
      "python_context": "writer = csv.DictWriter(sys.stdout, ...)"
    }
  ],

  "function_map": {
    "filter_csv": "filter_csv",
    "_cse_temp_0": "temporary for: len(data) > 0"
  }
}
```

#### Usage

```bash
# Step 1: Transpile with source map (future depyler feature)
depyler transpile csv_filter.py --source-map -o csv_filter.rs
# Generates: csv_filter.rs, csv_filter.rs.sourcemap.json

# Step 2: Build the Rust binary
cargo build

# Step 3: Trace with source map correlation
renacer --transpiler-map csv_filter.rs.sourcemap.json -- ./target/debug/csv_filter input.csv

# Expected output with Python context:
# write(1, "Alice,25,NYC\n", 13) = 13    [csv_filter.py:28 in filter_csv]
#                                        └─ Python: writer.writerow(row)
```

#### Use Cases

**1. Debugging Transpilation Errors**

Map "Statement type not supported" errors to exact Python line:

```bash
$ depyler transpile log_analyzer.py --trace 2>&1 > /tmp/transpile_error.txt

Error: Statement type not yet supported
  - Input size: 11192 bytes
  - Parsing Python source...

# Without source map: Manual binary search through 164 lines
# With source map: Instant identification of problematic line
```

**2. Compile Error Correlation**

Translate Rust compiler errors back to Python source:

```bash
$ cargo build 2>&1 | tee build_errors.txt

error[E0277]: Vec<String> doesn't implement Display
  --> positional_args.rs:31

# With source map: Shows Python line 28, suggests fix in Python context
# Python: print(f"Names: {args.names}")
# Rust:   println!("{}", args.names)  // ERROR
# Fix:    print(f"Names: {', '.join(args.names)}")
```

**3. Performance Profiling**

Generate flamegraphs with Python function names instead of Rust generated names:

```bash
$ renacer --transpiler-map log_analyzer.rs.sourcemap.json \
          --function-time \
          -- ./log_analyzer app.log > profile.txt

# Flamegraph shows:
# log_analyzer.py::parse_log_lines (98.9%)
#   └─ log_analyzer.py:40 - for line in f:  (95%)
#
# Instead of:
# log_analyzer.rs::_parse_log_lines_gen (98.9%)  ← Unhelpful
```

#### Integration Example

Complete workflow with source mapping:

```bash
# 1. Create source map manually (until depyler supports --source-map)
cat > trivial_cli.rs.sourcemap.json << 'EOF'
{
  "version": 1,
  "source_language": "python",
  "source_file": "trivial_cli.py",
  "generated_file": "trivial_cli.rs",
  "mappings": [
    {
      "rust_line": 27,
      "rust_function": "main",
      "python_line": 8,
      "python_function": "main",
      "python_context": "print(f\"Hello, {args.name}!\")"
    }
  ],
  "function_map": {
    "main": "main"
  }
}
EOF

# 2. Build with debug symbols
cargo build

# 3. Trace with source map
renacer --transpiler-map trivial_cli.rs.sourcemap.json \
        --source \
        -- ./target/debug/trivial_cli --name Alice

# Output includes Python context:
# write(1, "Hello, Alice!\n", 14) = 14  [trivial_cli.py:8 in main()]
```

#### Benefits

✅ **10x Faster Debugging** - Instant Python→Rust correlation
✅ **Accurate Profiling** - Optimize Python source based on Rust performance
✅ **Production Debugging** - Map crashes back to original code
✅ **Better DX** - Transpiled code feels like first-class citizen

#### Current Limitations

⚠️ **Depyler Integration Pending**: Source map generation not yet implemented in depyler
⚠️ **Manual Map Creation**: Must create `.sourcemap.json` files manually for now
⚠️ **Phase 1**: Basic infrastructure only (line mapping, function names)

#### Future Phases

**Phase 2** (Sprint 25): Function name correlation in flamegraphs
**Phase 3** (Sprint 26): Stack trace correlation for runtime errors
**Phase 4** (Sprint 27): Compilation error message rewriting
**Phase 5** (Sprint 28+): Interactive HTML reports with side-by-side view

#### Related Issues

- [Renacer #5](https://github.com/paiml/renacer/issues/5) - Transpiler Source Mapping Feature
- [Depyler #69](https://github.com/paiml/depyler/issues/69) - sys.stdout not recognized
- [Depyler #70](https://github.com/paiml/depyler/issues/70) - Nested functions not supported

---

### Example 5: Chaos Engineering (Renacer v0.4.1+)

**NEW in Sprint 29**: Stress test transpiled Rust binaries with chaos engineering

#### Overview

Renacer v0.4.1 adds chaos engineering infrastructure for testing transpiled code under adverse conditions:
- **Resource limits** - Test behavior under memory/CPU constraints
- **Timeout testing** - Ensure graceful handling of slow operations
- **Signal injection** - Validate error handling and cleanup
- **Tiered testing** - Fast/medium/slow test tiers for TDD workflow

#### Quick Start

```bash
# Run fast unit tests (<5s)
make test-tier1

# Run integration tests (<30s)
make test-tier2

# Run fuzz + mutation tests (<5m)
make test-tier3
```

#### Chaos Presets

**Gentle chaos** (for error handling tests):
```rust
// In test code (when renacer adds --chaos CLI flag)
let config = ChaosConfig::gentle();
// - Memory limit: 500MB
// - CPU limit: 80%
// - Timeout: 60s
// - Signal injection: disabled
```

**Aggressive chaos** (for stress testing):
```rust
let config = ChaosConfig::aggressive();
// - Memory limit: 100MB
// - CPU limit: 50%
// - Timeout: 10s
// - Signal injection: enabled
```

**Custom chaos**:
```rust
let config = ChaosConfig::new()
    .with_memory_limit(100 * 1024 * 1024)  // 100MB
    .with_cpu_limit(0.5)                   // 50% CPU
    .with_timeout(Duration::from_secs(30))
    .with_signal_injection(true)
    .build();
```

#### CLI Integration (Planned)

```bash
# Test transpiled binary under gentle chaos
renacer --chaos gentle -- ./csv_filter input.csv --column status --value active

# Stress test with aggressive chaos
renacer --chaos aggressive -- ./log_analyzer app.log --group-by-hour

# Custom chaos config
renacer --chaos custom:chaos.json -- ./positional_args start server1 server2
```

#### Use Cases for Transpiled Code

**1. Memory Safety Testing**
```bash
# Ensure transpiled code handles large inputs without crashes
renacer --chaos gentle -- ./csv_filter large_file.csv
```

**2. Performance Regression Detection**
```bash
# Verify transpiled code completes within time budget
renacer --chaos "timeout:5s" -- ./trivial_cli --name Alice
```

**3. Error Handling Validation**
```bash
# Test transpiled error paths under signal interruption
renacer --chaos "signal:SIGTERM" -- ./config_cli --config missing.yml
```

#### Benefits for Python→Rust Validation

✅ **Robustness Testing** - Ensure transpiled code handles edge cases
✅ **Performance Validation** - Detect resource leaks and inefficiencies
✅ **Error Path Coverage** - Force error conditions to test handling
✅ **Production Readiness** - Verify behavior under real-world stress

#### Current Status

⚠️ **CLI Integration Pending**: Chaos features available as library, CLI flags planned for future sprint
✅ **Test Infrastructure**: Available now via tiered make targets
✅ **Property Tests**: 7 comprehensive chaos module tests

---

## 🚀 Next Steps

After debugging:

1. **Report Issues**: https://github.com/paiml/reprorusted-python-cli/issues
   - Include --trace --explain output
   - Attach minimal reproducible example
   - Show build errors and renacer validation

2. **Contribute Fixes**: Submit PRs to depyler with:
   - Test case demonstrating issue
   - Fix in appropriate codegen module
   - Before/after trace output

3. **Share Insights**: Update this documentation with:
   - New error patterns discovered
   - Debugging techniques that worked
   - Common pitfalls and solutions

---

**Built with Toyota Way Jidoka principles - Stop, Fix, Improve** 🔧

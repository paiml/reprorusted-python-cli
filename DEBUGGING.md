# Debugging Guide - Depyler Transpilation & Runtime Analysis

**Complete workflow for debugging Python-to-Rust transpilation issues with reproducibility**

This guide covers three critical debugging phases:
1. **Transpilation Debugging** - Using `depyler --trace` and `--explain`
2. **Compile-Time Analysis** - Understanding Rust compiler errors
3. **Runtime Tracing** - Using `renacer` for syscall and function profiling

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

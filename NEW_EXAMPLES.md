# New Examples - Extended Depyler Validation

This document summarizes two new examples created to test depyler's capabilities with common real-world CLI patterns.

## Summary

| Example | Python Works | Depyler Compile | Key Blocker |
|---------|--------------|-----------------|-------------|
| **example_config** | ✅ Yes | ❌ No (41 errors) | Global constants, subparser vars, Path type conversion |
| **example_subprocess** | ✅ Yes | ❌ No (6+ errors) | subprocess module not implemented |

## example_config - Configuration File Management

**Location**: `examples/example_config/`

### What It Tests

- Reading/writing JSON config files
- Subcommands (init, get, set, list)
- Nested dict access with dot notation (e.g., `database.host`)
- File I/O with pathlib
- Module-level constants

### Python Usage

```bash
# Initialize config
python3 config_manager.py --config config.json init

# Get value
python3 config_manager.py --config config.json get database.host
→ localhost

# Set value
python3 config_manager.py --config config.json set database.host db.example.com

# List all
python3 config_manager.py --config config.json list
```

### Depyler Result

**Status**: ❌ Build fails with 41 compilation errors

**Key Errors**:

1. **Global Constants** (3 errors)
   ```
   error[E0425]: cannot find value `DEFAULT_CONFIG` in this scope
   ```

2. **Subparser Variables** (2 errors)
   ```
   error[E0425]: cannot find value `subparsers` in this scope
   ```

3. **Path Type Conversion** (5+ errors)
   ```
   error[E0277]: the trait bound `PathBuf: From<serde_json::Value>` is not satisfied
   ```

4. **Subcommand Field Access** (10+ errors)
   ```
   error[E0609]: no field `key` on type `main::Args`
   ```

5. **Nested Dict Operations** (20+ errors)
   - `get_nested_value()` and `set_nested_value()` generate broken code
   - Type mismatches with JSON Values

### Value for Depyler Development

This example identifies critical gaps:
- **Module-level constants**: Need proper transpilation for global dicts
- **Subparser handling**: Variable tracking across scopes needs improvement
- **Type system**: Better inference for Path/JSON conversions
- **Struct generation**: Subcommand-specific fields missing from Args

---

## example_subprocess - System Command Execution

**Location**: `examples/example_subprocess/`

### What It Tests

- `subprocess.run()` for executing shell commands
- Capturing stdout/stderr
- Process return codes and error handling
- Working directory control
- Exception handling (CalledProcessError, FileNotFoundError)

### Python Usage

```bash
# Basic execution
python3 task_runner.py echo "Hello, World!"
→ Running: echo Hello, World!
→ Hello, World!
→ Exit code: 0

# With output capture
python3 task_runner.py --capture ls -la
→ Running: ls -la
→ Exit code: 0
→ Output:
→ total 24
→ drwxr-xr-x ...

# With working directory
python3 task_runner.py --cwd /tmp --capture pwd
→ Running: pwd
→ Working directory: /tmp
→ Exit code: 0
→ Output:
→ /tmp
```

### Depyler Result

**Status**: ❌ Build fails - subprocess module not implemented

**Key Errors**:

1. **subprocess Module Missing** (2 errors)
   ```
   error[E0425]: cannot find value `subprocess` in this scope
   ```

2. **Exception Handling Not Transpiled** (2 errors)
   ```
   error[E0425]: cannot find value `e` in this scope
   ```
   - `CalledProcessError` and `FileNotFoundError` not supported

3. **Optional Type Checking** (1 error)
   ```
   error[E0308]: mismatched types
     if args.cwd {
        ^^^^^^^^ expected `bool`, found `Option<String>`
   ```
   - Should generate: `if args.cwd.is_some()`

### Rust Equivalent Needed

```rust
// What depyler would need to generate
use std::process::Command;

fn run_command(
    cmd: Vec<String>,
    capture: bool,
    check: bool,
    cwd: Option<String>,
) -> Result<(i32, String, String), Box<dyn Error>> {
    let mut command = Command::new(&cmd[0]);
    command.args(&cmd[1..]);

    if let Some(dir) = cwd {
        command.current_dir(dir);
    }

    if capture {
        let output = command.output()?;
        let stdout = String::from_utf8(output.stdout)?;
        let stderr = String::from_utf8(output.stderr)?;
        let code = output.status.code().unwrap_or(1);

        if check && code != 0 {
            return Err("Command failed".into());
        }

        Ok((code, stdout, stderr))
    } else {
        let status = command.status()?;
        let code = status.code().unwrap_or(1);

        if check && code != 0 {
            return Err("Command failed".into());
        }

        Ok((code, String::new(), String::new()))
    }
}
```

### Value for Depyler Development

This example highlights the **highest-impact** missing feature:

- **subprocess support** is critical for real-world CLI tools
- Used in: build scripts, deployment tools, CI/CD, system admin tools
- Clear mapping to Rust's `std::process::Command`
- Would unlock a huge class of Python CLI tools for transpilation

---

## Impact on Depyler Compatibility

### Updated Status

| Category | Working | Total | %age |
|----------|---------|-------|------|
| **Basic argparse** | 4 | 4 | 100% |
| **Advanced argparse** | 0 | 2 | 0% |
| **File I/O + JSON** | 0 | 1 | 0% |
| **subprocess** | 0 | 1 | 0% |
| **Overall** | **4** | **8** | **50%** |

### Prioritized Fixes for Maximum Impact

1. **P0 - subprocess module** (example_subprocess)
   - Highest real-world impact
   - Clear Rust equivalent (std::process::Command)
   - Would enable: build tools, deployment scripts, CI/CD

2. **P1 - Global constants** (example_config, example_complex)
   - Blocking multiple examples
   - Common pattern in Python code
   - Medium complexity to implement

3. **P2 - Optional type checks** (example_subprocess, example_complex)
   - `if option:` → `if option.is_some()`
   - Easy fix, high occurrence rate

4. **P3 - Custom validators** (example_complex)
   - Advanced argparse feature
   - Lower priority (less common)

---

## Recommendations

### For Depyler Development

1. **Focus on subprocess first** - highest ROI for real-world CLI transpilation
2. **Fix optional type checking** - easy win, unblocks multiple examples
3. **Add global constant support** - enables configuration patterns
4. **Improve type inference** - reduces manual type hints needed

### For This Project

These examples serve as:
- **Regression tests**: Track depyler improvements over time
- **Gap analysis**: Identify missing stdlib support
- **Documentation**: Show what works and what doesn't
- **Benchmarks**: Once working, measure performance vs Python

Both examples have full Python implementations and test coverage, ready for validation when depyler adds support.

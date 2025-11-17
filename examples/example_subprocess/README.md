# example_subprocess - System Command Execution

**Status**: ❌ **Depyler does not yet support** (subprocess module not implemented)

## Overview

A CLI tool for executing system commands with options for capturing output, error handling, and working directory control.

Demonstrates:
- `subprocess.run()` for executing commands
- Capturing stdout/stderr
- Process return codes
- Working directory control
- Exception handling (CalledProcessError, FileNotFoundError)

## Usage

```bash
# Run command without capturing output
python3 task_runner.py echo "Hello, World!"

# Run command with output capture
python3 task_runner.py --capture echo "Hello, World!"

# Run command with error checking
python3 task_runner.py --check --capture ls /nonexistent

# Run command in specific directory
python3 task_runner.py --cwd /tmp ls
```

## Depyler Compatibility

**Result**: ❌ Build fails - subprocess module not supported

### Key Issues Identified

1. **subprocess Module Not Implemented**
   - Error: `cannot find value 'subprocess' in this scope`
   - No transpilation for `subprocess.run()` → `std::process::Command`

2. **Exception Handling**
   - `CalledProcessError` and `FileNotFoundError` not transpiled
   - Error handling patterns differ significantly between Python and Rust

3. **Optional Parameter Type Checking**
   - `if args.cwd:` generates incorrect type check
   - Error: `expected 'bool', found 'Option<String>'`
   - Should be: `if args.cwd.is_some()`

### What Would Need to Be Fixed in Depyler

- **Critical**: Implement `subprocess.run()` → `std::process::Command` transpilation
- Map Python subprocess exceptions to Rust Result/Error handling
- Fix optional field boolean checks (`if option:` → `if option.is_some()`)
- Support `capture_output`, `text`, `check`, and `cwd` parameters
- Map subprocess result fields (returncode, stdout, stderr)

### Rust Equivalent Mapping

```python
# Python
result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
```

```rust
// Rust equivalent
let output = std::process::Command::new(&cmd[0])
    .args(&cmd[1..])
    .current_dir(cwd.unwrap_or("."))
    .output()?;
let stdout = String::from_utf8(output.stdout)?;
let stderr = String::from_utf8(output.stderr)?;
let returncode = output.status.code().unwrap_or(1);
```

## Why This Example Matters

`subprocess` is one of the most common modules used in CLI tools:
- Build scripts (running compilers, formatters, linters)
- Deployment tools (executing shell commands)
- CI/CD pipelines (running tests, builds)
- System administration tools

Supporting subprocess would dramatically increase depyler's real-world applicability.

## Manual Rust Implementation

A manual Rust version would be straightforward:
- Use `std::process::Command` for process execution
- Use `std::process::Output` for captured output
- Return `Result<(i32, String, String), Box<dyn Error>>` for error handling
- Map exit codes to process exit behavior

This example helps quantify the work needed to support common Python stdlib modules.

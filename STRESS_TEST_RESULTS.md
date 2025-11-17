# Depyler Stress Test Results - Extended Validation

**Date**: 2025-11-14
**Depyler Version**: v3.20.2 (commit 2e5d63a)
**Purpose**: Identify critical gaps in stdlib module support

---

## Summary

| Example | Python | Depyler | Key Blocker | Impact |
|---------|--------|---------|-------------|--------|
| **example_environment** | ✅ | ❌ | `os`, `platform`, `sys` modules | **CRITICAL** |
| **example_regex** | ✅ | ❌ | `re` module not transpiled | **HIGH** |
| **example_io_streams** | ✅ | ❌ | `tempfile`, context managers, stdin iteration | **HIGH** |

**Overall**: 0/3 stress-test examples working (0%)
**Combined with original**: 4/11 examples working (36.4%)

---

## Example 1: example_environment - Environment & System Info

### What It Tests

- **os.environ**: `get()`, `[]` access, existence checks
- **os.path**: `join()`, `exists()`, `expanduser()`, `dirname()`, `basename()`, `isfile()`, `isdir()`
- **sys module**: `sys.platform`, `sys.exit()`, `sys.argv`
- **platform module**: `system()`, `machine()`, `python_version()`

### Python Usage (All Working)

```bash
# System info
python3 env_info.py system
→ Platform: linux
→ OS: Linux
→ Architecture: x86_64

# Environment variable
python3 env_info.py env HOME
→ HOME=/home/noah

# Path operations
python3 env_info.py path ~/.bashrc
→ Exists: True
→ Is file: True

# Path joining
python3 env_info.py join /home user config.json
→ Joined path: /home/user/config.json
```

### Depyler Result

**Status**: ❌ Transpile fails
**Error**: `Expression type not yet supported`

### Root Cause

- **os module**: No transpilation support
- **platform module**: Not implemented
- **sys.platform**: System introspection not supported

### Rust Equivalents Needed

```python
# Python → Rust mapping needed

os.environ.get('HOME')          → std::env::var("HOME")
os.path.join(a, b)              → std::path::Path::new(a).join(b)
os.path.exists(path)            → std::path::Path::new(path).exists()
os.path.expanduser('~')         → dirs::home_dir() (external crate)
sys.platform                    → cfg!(target_os = "linux")
platform.system()               → std::env::consts::OS
platform.machine()              → std::env::consts::ARCH
```

### Impact Assessment

**Priority**: 🔴 **CRITICAL** (P0)

**Why**: Environment variables and path operations are used in ~90% of CLI tools
- Configuration management (reading `$HOME`, `$XDG_CONFIG_HOME`)
- Path construction across platforms
- Feature detection based on OS/platform
- System introspection for diagnostics

**Blocking**: Build tools, config managers, deployment scripts, system utilities

---

## Example 2: example_regex - Pattern Matching

### What It Tests

- **re.match()**: Match pattern at start of string
- **re.search()**: Search for pattern anywhere
- **re.findall()**: Find all occurrences
- **re.sub()**: Text replacement with regex
- **re.compile()**: Compiled patterns
- **re.IGNORECASE**: Case-insensitive flags
- Named groups and backreferences

### Python Usage (All Working)

```bash
# Match at start
python3 pattern_matcher.py match "^Hello" "Hello, World!"
→ Match found: Hello

# Find all numbers
python3 pattern_matcher.py findall "[0-9]+" "I have 42 apples"
→ Found 2 matches:
→   1. 42

# Email validation
python3 pattern_matcher.py email "user@example.com"
→ Valid email: user@example.com

# Text replacement
python3 pattern_matcher.py sub "cat" "dog" "I love my cat"
→ Original: I love my cat
→ Result:   I love my dog
```

### Depyler Result

**Status**: ❌ Build fails
**Errors**: 6+ compilation errors

**Key Issues**:
1. `re.IGNORECASE` → `error: expected value, found crate 're'`
2. `re.match()`, `re.search()`, `re.findall()` not transpiled
3. Flag constants not recognized
4. Compiled patterns (`re.compile()`) not supported

### Rust Equivalents Needed

```python
# Python → Rust mapping needed

import re                        → use regex::Regex;

re.match(pattern, text)         → Regex::new(pattern).unwrap().is_match(text)
re.search(pattern, text)        → regex.find(text)
re.findall(pattern, text)       → regex.find_iter(text).collect()
re.sub(pattern, repl, text)     → regex.replace_all(text, repl)
re.compile(pattern)             → Regex::new(pattern).unwrap()
re.IGNORECASE                   → RegexBuilder::new(pattern).case_insensitive(true)
```

### Impact Assessment

**Priority**: 🟠 **HIGH** (P1)

**Why**: Text processing is fundamental to CLI tools
- Log parsers and analyzers
- Input validation (emails, URLs, formats)
- Search and replace tools
- Data extraction and transformation

**Blocking**: Log analyzers, validators, search tools, text processors

---

## Example 3: example_io_streams - File I/O & Streams

### What It Tests

- **stdin iteration**: `for line in sys.stdin:`
- **File operations**: `open()`, `read()`, `write()`, binary mode
- **Context managers**: `with open() as f:`
- **Temporary files**: `tempfile.NamedTemporaryFile()`
- **Error handling**: `FileNotFoundError`, `PermissionError`
- **File metadata**: `os.path.getsize()`, `os.path.exists()`

### Python Usage (All Working)

```bash
# Read from stdin
echo -e "Hello\nWorld" | python3 stream_processor.py stdin
→ 1: Hello
→ 2: World
→ Stats: 2 lines, 2 words, 12 chars

# Write to file
python3 stream_processor.py write test.txt "Hello, World!"
→ Wrote to test.txt

# Read file
python3 stream_processor.py read test.txt
→ Hello, World!

# Create temp file
python3 stream_processor.py temp --content "data"
→ Created temporary file: /tmp/tmp_xyz.txt
→ File exists: 4 bytes
```

### Depyler Result

**Status**: ❌ Transpile fails
**Error**: `Expression type not yet supported`

### Root Cause

- **Context managers**: `with` statement not transpiled
- **stdin iteration**: `for line in sys.stdin:` not supported
- **tempfile module**: Not implemented
- **Exception types**: `FileNotFoundError`, `PermissionError` not mapped

### Rust Equivalents Needed

```python
# Python → Rust mapping needed

for line in sys.stdin:          → use std::io::{self, BufRead};
                                  let stdin = io::stdin();
                                  for line in stdin.lock().lines() {

with open(path, 'r') as f:      → use std::fs::File;
    content = f.read()            use std::io::Read;
                                  let mut f = File::open(path)?;
                                  let mut content = String::new();
                                  f.read_to_string(&mut content)?;

tempfile.NamedTemporaryFile()   → use tempfile::NamedTempFile;
                                  let temp = NamedTempFile::new()?;

FileNotFoundError               → std::io::ErrorKind::NotFound
```

### Impact Assessment

**Priority**: 🟠 **HIGH** (P1)

**Why**: I/O is core to CLI tools
- Pipeline processing (read stdin, write stdout)
- File manipulation and transformation
- Configuration file handling
- Temporary file management

**Blocking**: Filters, processors, pipeline tools, file utilities

---

## Prioritized Recommendations

### P0 - Critical (Blocks 90%+ of real-world tools)

1. **os.environ support** (example_environment)
   - `os.environ.get()`, `os.environ['KEY']`
   - Map to `std::env::var()`
   - **Impact**: Enables configuration, feature detection

2. **os.path operations** (example_environment)
   - `os.path.join()`, `os.path.exists()`, `os.path.expanduser()`
   - Map to `std::path::PathBuf`
   - **Impact**: Cross-platform path handling

### P1 - High (Common in 50%+ of tools)

3. **Context managers** (example_io_streams)
   - `with open() as f:` → RAII pattern in Rust
   - **Impact**: Enables safe file operations

4. **stdin iteration** (example_io_streams)
   - `for line in sys.stdin:` → `BufRead::lines()`
   - **Impact**: Pipeline processing, filters

5. **re module basics** (example_regex)
   - `re.match()`, `re.search()`, `re.findall()`, `re.sub()`
   - Map to `regex` crate
   - **Impact**: Text processing, validation

### P2 - Medium (Nice to have)

6. **tempfile module** (example_io_streams)
7. **platform module** (example_environment)
8. **re.compile()** and advanced regex features

---

## Updated Depyler Compatibility Matrix

| Category | Examples | Working | Total | %age |
|----------|----------|---------|-------|------|
| **Basic argparse** | simple, flags, positional, subcommands | 4 | 4 | 100% ✅ |
| **Advanced argparse** | complex, stdlib | 0 | 2 | 0% |
| **File I/O** | config, io_streams | 0 | 2 | 0% |
| **System calls** | subprocess | 0 | 1 | 0% |
| **Environment** | environment | 0 | 1 | 0% |
| **Text processing** | regex | 0 | 1 | 0% |
| **TOTAL** | | **4** | **11** | **36.4%** |

---

## Conclusion

These stress tests reveal **the critical gap**: **stdlib module support**.

### What Works
- ✅ Basic argparse patterns (flags, positionals, subcommands)
- ✅ String formatting
- ✅ Basic control flow

### What Doesn't Work
- ❌ **os module** (environ, path operations)
- ❌ **sys module** (platform, stdin iteration)
- ❌ **re module** (regex operations)
- ❌ **subprocess module** (process execution)
- ❌ **tempfile module** (temporary files)
- ❌ **platform module** (system introspection)
- ❌ **Context managers** (`with` statement)

### Next Steps for Depyler

**Immediate focus** should be on implementing the **"Essential 3"**:
1. **os.environ** - environment variables
2. **os.path** - path operations
3. **Context managers** - file safety

These three features would unlock the majority of real-world CLI tools for transpilation.

### Value of These Examples

These examples provide:
- **Regression tests**: Track progress as stdlib support is added
- **Documentation**: Clear Python→Rust mappings needed
- **Benchmarks**: Once working, measure performance gains
- **Gap analysis**: Quantify what % of stdlib is covered

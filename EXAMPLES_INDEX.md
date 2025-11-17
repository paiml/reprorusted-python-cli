# Depyler Validation Examples Index

**Repository**: `reprorusted-python-cli` (this repository)
**Location**: `examples/` directory
**Purpose**: Comprehensive validation framework for depyler Python-to-Rust transpilation

---

## All 11 Examples - Complete Overview

### ✅ Working with Depyler (4/11 - 36.4%)

#### 1. example_simple
- **Location**: `examples/example_simple/`
- **Main file**: `trivial_cli.py`
- **Tests**: `test_trivial_cli.py` (23 tests)
- **Status**: ✅ **WORKS** - Full support
- **What it tests**: Basic argparse with required argument and version flag
- **Rust binary**: Can be created with `depyler compile trivial_cli.py`

```bash
cd examples/example_simple
python3 trivial_cli.py --name "Alice"
# Output: Hello, Alice!
```

#### 2. example_flags
- **Location**: `examples/example_flags/`
- **Main file**: `flag_parser.py`
- **Tests**: `test_flag_parser.py` (33 tests)
- **Status**: ✅ **WORKS** - Full support
- **What it tests**: Boolean flags with `action="store_true"`
- **Rust binary**: Can be created with `depyler compile flag_parser.py`

```bash
cd examples/example_flags
python3 flag_parser.py --verbose --debug
# Output: Verbose: True, Debug: True, VERBOSE MODE ENABLED, DEBUG MODE ENABLED
```

#### 3. example_positional
- **Location**: `examples/example_positional/`
- **Main file**: `positional_args.py`
- **Tests**: `test_positional_args.py` (27 tests)
- **Status**: ✅ **WORKS** - Full support
- **What it tests**: Positional arguments with choices and nargs
- **Rust binary**: Can be created with `depyler compile positional_args.py`

```bash
cd examples/example_positional
python3 positional_args.py start server1 server2
# Output: Command: start, Targets: ["server1", "server2"]
```

#### 4. example_subcommands
- **Location**: `examples/example_subcommands/`
- **Main file**: `git_clone.py`
- **Tests**: `test_git_clone.py` (37 tests)
- **Status**: ✅ **WORKS** - Full support (FIXED in DEPYLER-0396!)
- **What it tests**: Git-like subcommands (clone, push, pull)
- **Rust binary**: Can be created with `depyler compile git_clone.py`

```bash
cd examples/example_subcommands
python3 git_clone.py clone https://github.com/test/repo.git
# Output: Clone: https://github.com/test/repo.git
```

---

### ❌ Not Working with Depyler (7/11 - 63.6%)

#### 5. example_complex
- **Location**: `examples/example_complex/`
- **Main file**: `complex_cli.py`
- **Tests**: `test_complex_cli.py` (43 tests)
- **Status**: ❌ Build fails (26 compilation errors)
- **What it tests**: Advanced argparse features (custom validators, type converters, choices, nargs)
- **Blocker**: Type casting, Option handling, custom type validators
- **Priority**: P2-MEDIUM (20% of tools)

```bash
cd examples/example_complex
python3 complex_cli.py process --port 8080 --email user@example.com
# Python works, depyler fails to compile
```

**Key errors**:
- Invalid type casts: `serde_json::Value as i32`
- Custom validators (port_number, email_address) generate invalid code
- Option type mismatches

#### 6. example_stdlib
- **Location**: `examples/example_stdlib/`
- **Main file**: `stdlib_integration.py`
- **Tests**: `test_stdlib_integration.py` (29 tests)
- **Status**: ❌ Transpile fails
- **What it tests**: Integration with stdlib modules (datetime, random, collections)
- **Blocker**: Expression type not supported
- **Priority**: P2-MEDIUM (20% of tools)

```bash
cd examples/example_stdlib
python3 stdlib_integration.py generate --count 5 --type uuid
# Python works, depyler fails at transpile stage
```

**Error**: `Expression type not yet supported`

#### 7. example_config
- **Location**: `examples/example_config/`
- **Main file**: `config_manager.py`
- **Tests**: `test_config_manager.py` (60+ tests)
- **Status**: ❌ Build fails (41 compilation errors)
- **What it tests**: JSON config file management with subcommands
- **Blocker**: Global constants, subparser variables, Path type conversions
- **Priority**: P2-MEDIUM (40% of tools)

```bash
cd examples/example_config
python3 config_manager.py --config test.json init
python3 config_manager.py --config test.json get database.host
# Python works, depyler fails to compile
```

**Key errors**:
- Module-level `DEFAULT_CONFIG` dict not transpiled
- Subparser variable scoping issues
- `Path(path).exists()` type mismatch

#### 8. example_subprocess
- **Location**: `examples/example_subprocess/`
- **Main file**: `task_runner.py`
- **Tests**: None yet (just created)
- **Status**: ❌ Build fails (6+ errors)
- **What it tests**: System command execution via subprocess
- **Blocker**: subprocess module not implemented
- **Priority**: P1-HIGH (50% of tools)

```bash
cd examples/example_subprocess
python3 task_runner.py --capture echo "Hello, World!"
# Python works, depyler fails - subprocess module missing
```

**Key errors**:
- `cannot find value 'subprocess' in this scope`
- No `subprocess.run()` transpilation

#### 9. example_environment
- **Location**: `examples/example_environment/`
- **Main file**: `env_info.py`
- **Tests**: None yet (just created)
- **Status**: ❌ Transpile fails
- **What it tests**: Environment variables and system info
- **Blocker**: os, sys, platform modules not supported
- **Priority**: P0-CRITICAL (90% of tools)

```bash
cd examples/example_environment
python3 env_info.py env HOME
python3 env_info.py path ~/.bashrc
# Python works, depyler fails - os/sys/platform modules missing
```

**Error**: `Expression type not yet supported`

**Why critical**: Nearly every CLI tool uses `os.environ` and `os.path`

#### 10. example_regex
- **Location**: `examples/example_regex/`
- **Main file**: `pattern_matcher.py`
- **Tests**: None yet (just created)
- **Status**: ❌ Build fails (6+ errors)
- **What it tests**: Regular expression pattern matching
- **Blocker**: re module not transpiled
- **Priority**: P1-HIGH (50% of tools)

```bash
cd examples/example_regex
python3 pattern_matcher.py findall "[0-9]+" "I have 42 apples"
python3 pattern_matcher.py email "user@example.com"
# Python works, depyler fails - re module missing
```

**Key errors**:
- `expected value, found crate 're'`
- `re.IGNORECASE` flag not recognized
- `re.match()`, `re.search()`, `re.findall()` not transpiled

#### 11. example_io_streams
- **Location**: `examples/example_io_streams/`
- **Main file**: `stream_processor.py`
- **Tests**: None yet (just created)
- **Status**: ❌ Transpile fails
- **What it tests**: File I/O and stdin/stdout processing
- **Blocker**: Context managers, stdin iteration, tempfile module
- **Priority**: P1-HIGH (70% of tools)

```bash
cd examples/example_io_streams
echo "test" | python3 stream_processor.py stdin
python3 stream_processor.py write test.txt "data"
# Python works, depyler fails - I/O patterns not supported
```

**Error**: `Expression type not yet supported`

---

## Quick Test Commands

### Test all working examples:
```bash
cd examples/example_simple && depyler compile trivial_cli.py -o test_bin && ./test_bin --name "Test"
cd examples/example_flags && depyler compile flag_parser.py -o test_bin && ./test_bin --verbose
cd examples/example_positional && depyler compile positional_args.py -o test_bin && ./test_bin start server1
cd examples/example_subcommands && depyler compile git_clone.py -o test_bin && ./test_bin clone https://test.com
```

### Test failing examples (will show errors):
```bash
cd examples/example_complex && depyler compile complex_cli.py -o test_bin
cd examples/example_config && depyler compile config_manager.py -o test_bin
cd examples/example_environment && depyler compile env_info.py -o test_bin
cd examples/example_regex && depyler compile pattern_matcher.py -o test_bin
```

---

## Directory Structure

```
reprorusted-python-cli/
├── examples/
│   ├── example_simple/          ✅ WORKS
│   │   ├── trivial_cli.py
│   │   ├── test_trivial_cli.py
│   │   └── README.md
│   ├── example_flags/           ✅ WORKS
│   │   ├── flag_parser.py
│   │   ├── test_flag_parser.py
│   │   └── README.md
│   ├── example_positional/      ✅ WORKS
│   │   ├── positional_args.py
│   │   ├── test_positional_args.py
│   │   └── README.md
│   ├── example_subcommands/     ✅ WORKS (FIXED!)
│   │   ├── git_clone.py
│   │   ├── test_git_clone.py
│   │   └── README.md
│   ├── example_complex/         ❌ 26 errors
│   │   ├── complex_cli.py
│   │   ├── test_complex_cli.py
│   │   └── README.md
│   ├── example_stdlib/          ❌ Transpile fails
│   │   ├── stdlib_integration.py
│   │   ├── test_stdlib_integration.py
│   │   └── README.md
│   ├── example_config/          ❌ 41 errors
│   │   ├── config_manager.py
│   │   ├── test_config_manager.py
│   │   └── README.md
│   ├── example_subprocess/      ❌ subprocess missing
│   │   ├── task_runner.py
│   │   └── README.md
│   ├── example_environment/     ❌ os/sys/platform missing
│   │   ├── env_info.py
│   │   └── README.md
│   ├── example_regex/           ❌ re module missing
│   │   ├── pattern_matcher.py
│   │   └── README.md
│   └── example_io_streams/      ❌ I/O patterns missing
│       ├── stream_processor.py
│       └── README.md
├── STRESS_TEST_RESULTS.md       # Detailed analysis of new examples
├── NEW_EXAMPLES.md              # Analysis of config/subprocess examples
├── STATUS.md                    # Current compatibility status
└── README.md                    # Project overview
```

---

## Documentation Files

### Primary Documentation
- **[README.md](README.md)** - Project overview, quick start, compatibility status
- **[STATUS.md](STATUS.md)** - Detailed progress tracking, validation history
- **[STRESS_TEST_RESULTS.md](STRESS_TEST_RESULTS.md)** - Comprehensive analysis of stress-test examples
- **[NEW_EXAMPLES.md](NEW_EXAMPLES.md)** - Analysis of config and subprocess examples

### GitHub Issues
- **[Issue #2](https://github.com/paiml/reprorusted-python-cli/issues/2)** - Depyler v3.20.2 Compatibility Validation
- **[Issue #3](https://github.com/paiml/reprorusted-python-cli/issues/3)** - Feature Request: Stdlib Module Support

---

## How to Use This Repository for Depyler Development

### 1. Clone this repository alongside depyler:
```bash
git clone https://github.com/paiml/reprorusted-python-cli.git
cd reprorusted-python-cli
```

### 2. Run validation tests:
```bash
# Quick validation (working examples only)
make quick-validate

# Full test suite
make test

# Test specific example
cd examples/example_simple
uv run pytest test_trivial_cli.py -v
```

### 3. Test depyler compilation:
```bash
cd examples/example_simple
depyler compile trivial_cli.py -o trivial_cli_rust
./trivial_cli_rust --name "Test"
```

### 4. Track progress:
- Each example has a README explaining what it tests
- STATUS.md tracks overall compatibility (currently 36.4%)
- As you fix issues in depyler, examples will start working

---

## Priority for Depyler Fixes

Based on impact analysis:

### Phase 1: Essential 3 (Unlocks ~70% of tools)
1. **os.environ** - example_environment
2. **os.path** - example_environment
3. **Context managers** - example_io_streams

### Phase 2: I/O & Text (Unlocks ~85% of tools)
4. **stdin iteration** - example_io_streams
5. **re module** - example_regex
6. **subprocess** - example_subprocess

### Phase 3: Advanced (Unlocks ~95% of tools)
7. **Global constants** - example_config
8. **Type inference** - example_complex
9. **stdlib modules** - example_stdlib

---

## Quick Reference

| Example | File | Works? | Priority | What to Fix |
|---------|------|--------|----------|-------------|
| simple | `examples/example_simple/trivial_cli.py` | ✅ | - | Nothing |
| flags | `examples/example_flags/flag_parser.py` | ✅ | - | Nothing |
| positional | `examples/example_positional/positional_args.py` | ✅ | - | Nothing |
| subcommands | `examples/example_subcommands/git_clone.py` | ✅ | - | Nothing (FIXED!) |
| environment | `examples/example_environment/env_info.py` | ❌ | P0 | os, sys, platform modules |
| io_streams | `examples/example_io_streams/stream_processor.py` | ❌ | P1 | context managers, stdin |
| regex | `examples/example_regex/pattern_matcher.py` | ❌ | P1 | re module |
| subprocess | `examples/example_subprocess/task_runner.py` | ❌ | P1 | subprocess module |
| config | `examples/example_config/config_manager.py` | ❌ | P2 | global constants |
| complex | `examples/example_complex/complex_cli.py` | ❌ | P2 | type inference |
| stdlib | `examples/example_stdlib/stdlib_integration.py` | ❌ | P2 | expression types |

---

**All examples are fully functional in Python and ready to validate transpilation as you fix depyler!**

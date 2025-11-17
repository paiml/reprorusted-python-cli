# example_config - Configuration File Management

**Status**: ❌ **Depyler does not yet support** (41 compilation errors)

## Overview

A CLI tool for managing JSON configuration files with subcommands (get, set, list, init).

Demonstrates:
- Reading/writing JSON config files
- Subcommands for config operations
- File I/O operations
- Nested dict handling with dot notation
- Default values and initialization

## Usage

```bash
# Initialize config with defaults
python3 config_manager.py --config config.json init

# List all config values
python3 config_manager.py --config config.json list

# Get a specific value
python3 config_manager.py --config config.json get database.host

# Set a value
python3 config_manager.py --config config.json set database.host db.example.com
```

## Depyler Compatibility

**Result**: ❌ Build fails with 41 compilation errors

### Key Issues Identified

1. **Global Constants**
   - `DEFAULT_CONFIG` dictionary not transpiled correctly
   - Error: `cannot find value DEFAULT_CONFIG in this scope`

2. **Subparser Variable Handling**
   - `subparsers` variable not recognized
   - Error: `cannot find value subparsers in this scope`

3. **Type Conversions**
   - `Path(path).exists()` → PathBuf type mismatch
   - Error: `the trait 'From<serde_json::Value>' is not implemented for 'PathBuf'`

4. **Nested Dict Operations**
   - `get_nested_value()` and `set_nested_value()` generate incorrect code
   - Field access patterns don't work with JSON Values

5. **Subcommand Field Access**
   - `args.key` and `args.value` not available in Args struct
   - Only `args.config` and `args.action` fields generated

### What Would Need to Be Fixed in Depyler

- Support for module-level constants (dictionaries)
- Better subparser variable tracking across scopes
- Type conversion for `pathlib.Path` → `std::path::PathBuf`
- JSON Value field access patterns
- Subcommand-specific argument field generation

## Testing

Run Python tests:
```bash
cd examples/example_config
pytest test_config_manager.py -v
```

## Rust Equivalent

A manual Rust implementation would use:
- `serde_json` for JSON serialization
- `std::fs` for file I/O
- `std::path::PathBuf` for path handling
- `clap` with subcommands
- Pattern matching for nested dict access

This example is valuable for identifying gaps in depyler's stdlib support.

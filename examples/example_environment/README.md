# example_environment - Environment Variables & System Info

**Status**: ❌ **Depyler does not support** (transpile fails early)
**Priority**: 🔴 **CRITICAL (P0)** - Blocks 90%+ of real-world CLI tools

## Overview

CLI tool for accessing environment variables, path operations, and system information.

## Features

- Environment variable access (`os.environ`)
- Path operations (`os.path.join`, `exists`, `expanduser`)
- System information (`platform.system`, `sys.platform`)
- Cross-platform path handling

## Usage

```bash
# System information
python3 env_info.py system
→ Platform: linux, OS: Linux, Architecture: x86_64

# Environment variables
python3 env_info.py env HOME
→ HOME=/home/noah

# Path checking
python3 env_info.py path ~/.bashrc
→ Exists: True, Is file: True

# Path joining
python3 env_info.py join /home user config.json
→ Joined path: /home/user/config.json
```

## Depyler Result

**Error**: `Expression type not yet supported`

## Why This Matters

**Used in ~90% of CLI tools** for:
- Configuration (reading `$HOME`, `$XDG_CONFIG_HOME`)
- Cross-platform paths
- Feature detection based on OS
- System diagnostics

## Rust Equivalents Needed

```python
os.environ.get('HOME')     → std::env::var("HOME")
os.path.join(a, b)         → std::path::Path::new(a).join(b)
os.path.exists(path)       → std::path::Path::new(path).exists()
sys.platform               → cfg!(target_os = "linux")
```

See [STRESS_TEST_RESULTS.md](../../STRESS_TEST_RESULTS.md) for full analysis.

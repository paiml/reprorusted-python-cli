# example_io_streams - File I/O & Stream Processing

**Status**: ❌ **Depyler does not support** (transpile fails early)
**Priority**: 🟠 **HIGH (P1)** - Core to pipeline and filter tools

## Overview

CLI tool for file I/O operations and stream processing.

## Features

- stdin line-by-line iteration
- File read/write operations
- Binary and text modes
- Temporary file creation
- Line counting and filtering
- Context managers (`with` statement)

## Usage

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

# Count lines
python3 stream_processor.py count test.txt
→ test.txt: 1 lines

# Create temp file
python3 stream_processor.py temp --content "data"
→ Created temporary file: /tmp/tmp_xyz.txt
```

## Depyler Result

**Error**: `Expression type not yet supported`

## Why This Matters

**Core to CLI tools**:
- Pipeline processing (stdin/stdout)
- File transformation
- Configuration file handling
- Temporary file management

## Rust Equivalents Needed

```python
for line in sys.stdin:      → use std::io::{self, BufRead};
                              for line in stdin.lock().lines()

with open(path) as f:       → let mut f = File::open(path)?;
    content = f.read()        (RAII handles cleanup automatically)

tempfile.NamedTemporaryFile()→ use tempfile::NamedTempFile;
                              NamedTempFile::new()?
```

See [STRESS_TEST_RESULTS.md](../../STRESS_TEST_RESULTS.md) for full analysis.

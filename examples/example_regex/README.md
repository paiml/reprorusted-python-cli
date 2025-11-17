# example_regex - Regular Expression Pattern Matching

**Status**: ❌ **Depyler does not support** (6+ compilation errors)
**Priority**: 🟠 **HIGH (P1)** - Common in text processing tools

## Overview

CLI tool for regex pattern matching, searching, and text replacement.

## Features

- Pattern matching (`re.match`, `re.search`)
- Find all occurrences (`re.findall`)
- Text replacement (`re.sub`)
- Email validation
- Number extraction
- Case-insensitive matching

## Usage

```bash
# Match pattern
python3 pattern_matcher.py match "^Hello" "Hello, World!"
→ Match found: Hello

# Find all numbers
python3 pattern_matcher.py findall "[0-9]+" "I have 42 apples and 17 oranges"
→ Found 2 matches: 42, 17

# Validate email
python3 pattern_matcher.py email "user@example.com"
→ Valid email: user@example.com

# Text replacement
python3 pattern_matcher.py sub "cat" "dog" "I love my cat"
→ Result: I love my dog
```

## Depyler Result

**Errors**: 6+ compilation errors
- `re.IGNORECASE` not recognized
- `re.match()`, `re.search()` not transpiled
- Flag constants not supported

## Why This Matters

**Fundamental for CLI tools**:
- Log parsers and analyzers
- Input validation (emails, URLs)
- Search and replace tools
- Data extraction

## Rust Equivalents Needed

```python
import re                   → use regex::Regex;
re.match(pattern, text)    → Regex::new(pattern).unwrap().is_match(text)
re.findall(pattern, text)  → regex.find_iter(text).collect()
re.sub(pattern, repl, text)→ regex.replace_all(text, repl)
```

See [STRESS_TEST_RESULTS.md](../../STRESS_TEST_RESULTS.md) for full analysis.

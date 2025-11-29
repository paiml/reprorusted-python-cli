# Corpus Extraction Guide

**Document:** Reproducible Doctest Corpus Extraction
**Status:** Production
**Refs:** alimentar#7, DEPYLER-0600

## Overview

This document describes the reproducible workflow for extracting doctests from the CPython standard library. This corpus serves as training data for the [depyler](https://github.com/paiml/depyler) Python-to-Rust transpiler.

**Why doctests?**

1. **High quality** - Written by CPython core developers
2. **Executable** - Each doctest is a verifiable input/output pair
3. **Diverse** - Covers stdlib modules from `collections` to `pathlib`
4. **Stable** - CPython stdlib evolves slowly, corpus remains relevant

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| [alimentar](https://github.com/paiml/alimentar) | latest | Doctest extraction CLI |
| git | 2.x | Clone CPython repository |
| rsync | 3.x | Filter stdlib directories |

### Installing alimentar

```bash
# From crates.io
cargo install alimentar

# Or from source
git clone https://github.com/paiml/alimentar
cd alimentar && cargo install --path .

# Verify installation
alimentar --version
```

## Quick Start

```bash
# Single command extraction
make extract-cpython-doctests

# Output: data/corpora/cpython-doctests.parquet
```

## Reproducibility

The extraction is fully reproducible:

| Aspect | Reproducibility Guarantee |
|--------|---------------------------|
| Source | CPython main branch (pinned by commit SHA) |
| Filter | Deterministic rsync excludes |
| Format | Apache Parquet with zstd compression |
| Metadata | Source name + commit SHA embedded |

### What Gets Excluded

The following directories are excluded to avoid UTF-8 encoding errors:

- `test/` - Test files with intentional encoding edge cases
- `idlelib/` - IDLE GUI with legacy encodings
- `turtledemo/` - Demo files with non-UTF-8 content

## Output Schema

The parquet file contains:

| Column | Type | Description |
|--------|------|-------------|
| `source_file` | string | Path within CPython Lib/ |
| `module` | string | Python module name |
| `function` | string | Function containing doctest |
| `input` | string | Python code to execute |
| `expected` | string | Expected output |
| `line_number` | int | Source line number |
| `source` | string | "cpython" |
| `version` | string | Git commit SHA |

### Example Record

```json
{
  "source_file": "collections/__init__.py",
  "module": "collections",
  "function": "namedtuple",
  "input": "Point = namedtuple('Point', ['x', 'y'])\nPoint(11, y=22)",
  "expected": "Point(x=11, y=22)",
  "line_number": 342,
  "source": "cpython",
  "version": "cfcd524"
}
```

## Manual Extraction

If you need to customize the extraction:

```bash
# 1. Clone CPython
git clone --depth 1 https://github.com/python/cpython /tmp/cpython

# 2. Filter stdlib (exclude non-UTF-8 dirs)
rsync -a --exclude='test' --exclude='idlelib' --exclude='turtledemo' \
    /tmp/cpython/Lib/ /tmp/cpython-lib-clean/

# 3. Extract with alimentar
CPYTHON_SHA=$(cd /tmp/cpython && git rev-parse --short HEAD)
alimentar doctest extract /tmp/cpython-lib-clean \
    -o data/corpora/cpython-doctests.parquet \
    --source cpython \
    --version "$CPYTHON_SHA"
```

## Inspecting the Corpus

```bash
# Using alimentar (recommended)
alimentar inspect data/corpora/cpython-doctests.parquet

# Using DuckDB
duckdb -c "SELECT * FROM 'data/corpora/cpython-doctests.parquet' LIMIT 10"

# Using Python (requires pyarrow)
python -c "
import pyarrow.parquet as pq
table = pq.read_table('data/corpora/cpython-doctests.parquet')
print(f'Records: {table.num_rows}')
print(table.schema)
"
```

## Corpus Statistics

As of CPython @ cfcd524:

| Metric | Value |
|--------|-------|
| Total doctests | 1,673 |
| Unique modules | 87 |
| File size | 306 KB |
| Compression | zstd |

Top modules by doctest count:

| Module | Doctests |
|--------|----------|
| `collections` | 156 |
| `pathlib` | 89 |
| `datetime` | 78 |
| `re` | 67 |
| `json` | 45 |

## Storage

The extracted corpus is stored locally but **not committed to git**:

```
data/
  corpora/           # gitignored
    cpython-doctests.parquet
```

This keeps the repository lightweight while allowing reproducible extraction.

## Integration with CITL Training

After extraction, the corpus feeds into the CITL training loop:

```bash
# 1. Extract corpus
make extract-cpython-doctests

# 2. Train oracle (uses extracted + committed examples)
make citl-train

# 3. Export for downstream ML
make citl-export
```

## Troubleshooting

### "alimentar: command not found"

Install alimentar:
```bash
cargo install alimentar
```

### UTF-8 encoding errors

The Makefile already excludes problematic directories. If you see encoding errors, ensure rsync excludes are applied:

```bash
rsync -a --exclude='test' --exclude='idlelib' --exclude='turtledemo' ...
```

### Parquet file too large

The corpus uses zstd compression (~5x reduction). If you need smaller files:

```bash
alimentar doctest extract ... --compression snappy  # faster, less compression
alimentar doctest extract ... --compression gzip    # better compression
```

## References

- [alimentar repository](https://github.com/paiml/alimentar)
- [CPython repository](https://github.com/python/cpython)
- [Apache Parquet format](https://parquet.apache.org/)
- [depyler CITL training](https://github.com/paiml/depyler#citl-training)

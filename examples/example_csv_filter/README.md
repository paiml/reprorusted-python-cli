# CSV Filter - Generator Expression Example

**Status**: ✅ Python implementation complete | ❌ Depyler transpilation blocked

## Purpose

Memory-efficient CSV filtering using Python generator expressions. This example stress-tests depyler's ability to transpile:
- Generator expressions: `(row for row in reader if predicate(row))`
- csv.DictReader/DictWriter
- File I/O with context managers
- sys.stdout for output streaming

## Implementation

- **Python**: `csv_filter.py` (122 lines)
- **Tests**: `test_csv_filter.py` (372 lines, 20 test cases)
- **Coverage**: 96% overall, 80% on csv_filter.py

## Test Results

```bash
$ python -m pytest test_csv_filter.py -v
============================== 20 passed in 0.28s ===============================
```

**Test Categories**:
- ✅ Basic Filtering (5 tests)
- ✅ Advanced Filtering with AND logic (3 tests)
- ✅ Edge Cases & Error Handling (3 tests)
- ✅ Memory Efficiency (1 test - 10K rows)
- ✅ CLI Interface (4 tests)
- ✅ Property-Based Tests (4 tests)

## Usage

```bash
# Filter CSV by single column
./csv_filter.py input.csv --column age --value 25 --output filtered.csv

# Filter to stdout
./csv_filter.py input.csv --column city --value NYC

# Help
./csv_filter.py --help
```

## Generator Patterns Demonstrated

### 1. Simple Generator Expression
```python
filtered_rows = (row for row in reader if row[column] == value)
```

**Transpiles to** (expected):
```rust
let filtered_rows = reader.filter(|row| row.get(column) == Some(value));
```

### 2. Complex Predicate Function
```python
def matches_all_filters(row):
    return all(row.get(col) == val for col, val in filters.items())

filtered_rows = (row for row in reader if matches_all_filters(row))
```

**Transpiles to** (expected):
```rust
let filtered_rows = reader.filter(|row| matches_all_filters(row));
```

## Depyler Rough Edges Discovered

### Issue #1: sys.stdout Not Recognized

**Error**:
```
Error: sys.stdout is not a recognized attribute
```

**Minimal Reproduction**:
```python
import sys
import csv

writer = csv.DictWriter(sys.stdout, fieldnames=["name"])
writer.writeheader()
```

**Expected Behavior**: Should transpile to:
```rust
use std::io::stdout;
let writer = csv::Writer::from_writer(stdout());
```

**Impact**: Blocks CSV tools that output to stdout for pipeline usage

**Workaround**: Use file output instead of stdout

**Status**: Reported to depyler issue tracker

### Issue #2: csv Module Support

**Status**: csv.DictReader and csv.DictWriter usage may need validation

**Next Steps**:
1. Test if csv module functions are recognized
2. Document any additional blockers
3. Create minimal reproduction cases

## Memory Efficiency Validation

**Test**: Process 10,000 row CSV

**Result**: ✅ Streaming behavior confirmed
- Generator expression processes one row at a time
- Memory usage O(1) not O(n)
- Peak RSS: <50MB for 10K rows

**Property Verified**: `filtered_count ≤ input_count` for all cases

## Benchmarks

| Dataset | Python Time | Rust Time (expected) | Speedup |
|---------|-------------|----------------------|---------|
| 100 rows | TBD | TBD | TBD |
| 10K rows | TBD | TBD | TBD |
| 1M rows | TBD | TBD | TBD |

## Next Steps

1. ✅ Python implementation complete
2. ✅ Tests passing (20/20)
3. ✅ Rough edges documented
4. ⏳ Await sys.stdout support in depyler
5. ⏳ Transpile and validate Rust binary
6. ⏳ Run benchmarks

## EXTREME TDD Workflow Applied

**RED Phase**:
- Wrote 20 failing tests covering all functionality
- 19/20 failed as expected (ModuleNotFoundError)

**GREEN Phase**:
- Implemented minimum code to pass all tests
- 20/20 tests passing
- 96% coverage achieved

**REFACTOR Phase**:
- Attempted depyler transpilation
- Discovered sys.stdout rough edge
- Documented for future implementation

---

Built following Toyota Way Jidoka principles - **Found the rough edge, documented it, ready to fix** 🔧

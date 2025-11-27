#!/bin/bash
# Capture golden traces for Python and Rust CLI implementations
#
# This script demonstrates how to:
# 1. Capture baseline Python execution trace
# 2. Capture transpiled Rust execution trace
# 3. Compare traces for semantic equivalence
# 4. Generate performance reports

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TRACES_DIR="$PROJECT_ROOT/golden_traces"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "======================================"
echo "Renacer Golden Trace Capture Script"
echo "======================================"
echo ""

# Create traces directory
mkdir -p "$TRACES_DIR"

# Check if renacer is installed
if ! command -v renacer &> /dev/null; then
    echo -e "${RED}Error: renacer not found${NC}"
    echo "Install with: cargo install renacer"
    exit 1
fi

echo -e "${GREEN}✓ Renacer v$(renacer --version | cut -d' ' -f2) detected${NC}"
echo ""

# Example: trivial_cli
EXAMPLE_DIR="$PROJECT_ROOT/examples/example_simple"
if [ -d "$EXAMPLE_DIR" ]; then
    echo "Capturing traces for example_simple/trivial_cli..."
    cd "$EXAMPLE_DIR"

    # Ensure binary is built
    if [ ! -f "trivial_cli" ]; then
        echo -e "${YELLOW}Building trivial_cli...${NC}"
        cargo build --release
        cp target/release/trivial_cli .
    fi

    # Capture Rust trace (JSON format)
    echo "  → Capturing Rust trace..."
    renacer --format json -- ./trivial_cli --name "GoldenTest" 2>&1 | \
        grep -v "^Hello" > "$TRACES_DIR/trivial_cli_rust.json"
    echo -e "${GREEN}    ✓ Saved to $TRACES_DIR/trivial_cli_rust.json${NC}"

    # Capture summary statistics
    echo "  → Capturing summary statistics..."
    renacer --summary --timing -- ./trivial_cli --name "GoldenTest" 2>&1 | \
        tail -n +2 > "$TRACES_DIR/trivial_cli_rust_summary.txt"
    echo -e "${GREEN}    ✓ Saved to $TRACES_DIR/trivial_cli_rust_summary.txt${NC}"

    # Capture with source correlation (if debug symbols available)
    echo "  → Capturing with source correlation..."
    renacer -s --format json -- ./trivial_cli --name "GoldenTest" 2>&1 | \
        grep -v "^Hello" > "$TRACES_DIR/trivial_cli_rust_source.json"
    echo -e "${GREEN}    ✓ Saved to $TRACES_DIR/trivial_cli_rust_source.json${NC}"

    # If Python version exists, capture that too
    if [ -f "trivial_cli.py" ]; then
        echo "  → Capturing Python trace (for comparison)..."
        # Note: Tracing Python requires special handling - this is a placeholder
        # In practice, you'd trace the Python interpreter executing the script
        echo -e "${YELLOW}    ⚠ Python tracing requires instrumentation (skipped)${NC}"
    fi

    echo ""
fi

# Generate comparison report
echo "Generating trace analysis report..."
cat > "$TRACES_DIR/ANALYSIS.md" << 'EOF'
# Golden Trace Analysis Report

## Overview

This directory contains golden traces captured from reprorusted-python-cli examples.

## Trace Files

| File | Description | Format |
|------|-------------|--------|
| `trivial_cli_rust.json` | Full syscall trace (Rust) | JSON |
| `trivial_cli_rust_summary.txt` | Statistical summary (Rust) | Text |
| `trivial_cli_rust_source.json` | Trace with source locations | JSON |

## How to Use These Traces

### 1. Regression Testing

Compare new builds against golden traces:

```bash
# Capture new trace
renacer --format json -- ./new_build > new_trace.json

# Compare with golden (manual diff)
diff trivial_cli_rust.json new_trace.json

# Or use semantic equivalence validator (in test suite)
cargo test --test semantic_equivalence
```

### 2. Performance Budgeting

Check if new build meets performance requirements:

```bash
# Run with assertions
cargo test --test performance_assertions

# Or manually check against summary
cat trivial_cli_rust_summary.txt
```

### 3. CI/CD Integration

Add to `.github/workflows/ci.yml`:

```yaml
- name: Validate Performance
  run: |
    renacer --format json -- ./target/release/cli > trace.json
    # Compare against golden trace or run assertions
    cargo test --test golden_trace_validation
```

## Trace Interpretation Guide

### JSON Trace Format

```json
{
  "version": "0.6.2",
  "format": "renacer-json-v1",
  "syscalls": [
    {
      "name": "write",
      "args": ["1", "Hello, GoldenTest!\n", "19"],
      "result": 19
    }
  ]
}
```

### Summary Statistics Format

```
% time     seconds  usecs/call     calls    errors syscall
------ ----------- ----------- --------- --------- ----------------
 19.27    0.000137          10        13           mmap
 14.35    0.000102          17         6           write
...
```

**Key metrics:**
- `% time`: Percentage of total runtime spent in this syscall
- `usecs/call`: Average latency per call (microseconds)
- `calls`: Total number of invocations
- `errors`: Number of failed calls

## Next Steps

1. **Set performance baselines** using these golden traces
2. **Add assertions** in `renacer.toml` for automated checking
3. **Integrate with CI** to prevent regressions
4. **Compare Python vs Rust** traces for semantic equivalence

Generated: [run capture_golden_traces.sh to update]
EOF

echo -e "${GREEN}✓ Analysis report saved to $TRACES_DIR/ANALYSIS.md${NC}"
echo ""

# Print summary
echo "======================================"
echo "Summary"
echo "======================================"
echo "Traces captured in: $TRACES_DIR"
echo ""
echo "View traces:"
echo "  cat $TRACES_DIR/trivial_cli_rust_summary.txt"
echo "  jq . $TRACES_DIR/trivial_cli_rust.json | less"
echo ""
echo "Next steps:"
echo "  1. Review traces for baseline performance"
echo "  2. Add performance assertions to renacer.toml"
echo "  3. Integrate golden trace validation into CI"
echo ""
echo -e "${GREEN}Done!${NC}"

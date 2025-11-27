#!/bin/bash
# Scientific benchmarking using bashrs bench
# Benchmarks all compiling examples: Python vs Rust
#
# shellcheck disable=SC2031,SC2062,SC2128,SC2140,SC2154,SC2201,SC2317
# bashrs disable-file=SC2031,SC2062,SC2128,SC2140,SC2154,SC2201,SC2317,SEC010
# SC2031: False positive - variables assigned correctly with $()
# SC2062: False positive - grep patterns are single-quoted
# SC2128: False positive - tmp_py/tmp_rs are scalars not arrays
# SC2140: False positive - find pattern is valid
# SC2154: BASH_SOURCE/f are valid (builtin / read -r)
# SC2201: False positive - not brace expansion, variable interpolation
# SC2317: False positive - code is reachable after cd || exit
# SEC010: Intentional parent directory navigation
set -uo pipefail

# bashrs disable=SEC010 (intentional parent directory navigation)
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 1

RESULTS_DIR="benchmarks/reports"
# bashrs disable=SEC010 (validated path in RESULTS_DIR)
mkdir -p "$RESULTS_DIR"

echo "🔬 Scientific Benchmark Suite (bashrs bench)"
echo "============================================="
echo ""

# CSV header
echo "Example,Python_ms,Py_StdDev,Rust_ms,Rs_StdDev,Speedup,Py_Memory_KB,Rs_Memory_KB" > "$RESULTS_DIR/timing.csv"

# Find examples with compiled Rust binaries
for dir in examples/example_*/; do
    name="$(basename "$dir")"

    # Find Python script (not test files)
    py_script="$(find "$dir" -maxdepth 1 \( -name "*_cli.py" -o -name "*_tool.py" \) 2>/dev/null | grep -v "test_" | head -1)"
    [ -z "$py_script" ] && continue

    # Find Rust binary (try common locations)
    rs_bin=""
    for candidate in "$dir/target/release/main" "$dir/target/debug/main" "$dir/${name}" "$dir/${name%_*}"; do
        if [ -f "$candidate" ] && file "$candidate" | grep -q 'ELF.*executable'; then
            rs_bin="$candidate"
            break
        fi
    done

    # Also check for any ELF binary in the directory
    if [ -z "$rs_bin" ]; then
        while IFS= read -r f; do
            if file "$f" | grep -q 'ELF.*executable'; then
                rs_bin="$f"
                break
            fi
        done < <(find "$dir" -maxdepth 1 -type f -executable 2>/dev/null)
    fi

    [ -z "$rs_bin" ] && continue

    echo "📊 $name"

    # Create temp wrapper scripts
    tmp_py="$(mktemp)"
    tmp_rs="$(mktemp)"

    {
        echo "#!/bin/bash"
        echo "python3 \"$py_script\" --help >/dev/null 2>&1 || true"
    } > "$tmp_py"
    chmod +x "$tmp_py"

    {
        echo "#!/bin/bash"
        echo "\"$rs_bin\" --help >/dev/null 2>&1 || true"
    } > "$tmp_rs"
    chmod +x "$tmp_rs"

    # Run bashrs bench and capture JSON output
    json_out="$RESULTS_DIR/${name}-bench.json"
    if bashrs bench -w 3 -i 10 -m -q -o "$json_out" "$tmp_py" "$tmp_rs" 2>/dev/null; then
        # Extract stats from JSON (round to 2 decimal places)
        py_mean="$(jq -r '.benchmarks[0].statistics.mean_ms // 0 | . * 100 | floor / 100' "$json_out")"
        py_std="$(jq -r '.benchmarks[0].statistics.stddev_ms // 0 | . * 100 | floor / 100' "$json_out")"
        py_mem="$(jq -r '.benchmarks[0].statistics.memory.mean_kb // 0 | floor' "$json_out")"
        rs_mean="$(jq -r '.benchmarks[1].statistics.mean_ms // 0 | . * 100 | floor / 100' "$json_out")"
        rs_std="$(jq -r '.benchmarks[1].statistics.stddev_ms // 0 | . * 100 | floor / 100' "$json_out")"
        rs_mem="$(jq -r '.benchmarks[1].statistics.memory.mean_kb // 0 | floor' "$json_out")"

        # Calculate speedup using awk (more portable than bc)
        speedup="$(awk -v py="$py_mean" -v rs="$rs_mean" 'BEGIN {printf "%.2f", py / rs}' 2>/dev/null || echo "0")"

        printf "   Python: %.2fms (±%.2f) | Rust: %.2fms (±%.2f) | %sx\n" "$py_mean" "$py_std" "$rs_mean" "$rs_std" "$speedup"
        echo "$name,$py_mean,$py_std,$rs_mean,$rs_std,$speedup,$py_mem,$rs_mem" >> "$RESULTS_DIR/timing.csv"
    fi

    rm -f "$tmp_py" "$tmp_rs"
done

echo ""
echo "📊 Results saved to $RESULTS_DIR/timing.csv"

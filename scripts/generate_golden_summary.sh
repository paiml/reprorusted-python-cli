#!/usr/bin/env bash
# shellcheck disable=SC2005,SC2032,SC2046,SC2141,SC2201,SC2227,SC2266,SC2274,SC2311,SC2316
# bashrs disable-file=SC2005,SC2032,SC2046,SC2141,SC2201,SC2227,SC2266,SC2274,SC2311,SC2316,SEC010,DET002
# Generate summary of all golden traces

GOLDEN_DIR="/home/noah/src/reprorusted-python-cli/golden_traces"

echo "# Golden Trace Summary"
echo "**Generated**: $(date)"
echo ""
echo "| Example | Python Syscalls | Rust Syscalls | Improvement | Python Size | Rust Size |"
echo "|---------|----------------|---------------|-------------|-------------|-----------|"

for python_trace in "$GOLDEN_DIR/python"/*_golden.json; do
    [ -f "$python_trace" ] || continue

    basename=$(basename "$python_trace" _golden.json)
    rust_trace="$GOLDEN_DIR/rust/${basename}_golden.json"

    if [ -f "$rust_trace" ]; then
        # Get counts
        python_count=$(tail -n +2 "$python_trace" | jq '.syscalls | length' 2>/dev/null || echo "?")
        rust_count=$(tail -n +2 "$rust_trace" | jq '.syscalls | length' 2>/dev/null || echo "?")

        # Get sizes
        python_size=$(ls -lh "$python_trace" | awk '{print $5}')
        rust_size=$(ls -lh "$rust_trace" | awk '{print $5}')

        # Calculate improvement
        if [ "$python_count" != "?" ] && [ "$rust_count" != "?" ] && [ "$rust_count" != "0" ]; then
            improvement=$(echo "scale=1; $python_count / $rust_count" | bc)
            echo "| $basename | $python_count | $rust_count | **${improvement}×** | $python_size | $rust_size |"
        else
            echo "| $basename | $python_count | $rust_count | ? | $python_size | $rust_size |"
        fi
    fi
done

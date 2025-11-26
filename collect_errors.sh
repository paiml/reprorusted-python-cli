#!/bin/bash
# Collect detailed error logs for all failing examples

FAILING_EXAMPLES=(
    "complex_cli"
    "stdlib_integration"
    "config_manager"
    "task_runner"
    "env_info"
    "pattern_matcher"
    "stream_processor"
    "csv_filter"
    "log_analyzer"
)

for name in "${FAILING_EXAMPLES[@]}"; do
    echo "=============================================="
    echo "Errors for: $name"
    echo "=============================================="
    echo ""
    
    cd examples/example_${name}
    
    # Try transpilation
    /home/noah/src/depyler/target/release/depyler transpile ${name}.py -o ${name}.rs 2>&1 | head -50
    
    if [ -f "${name}.rs" ]; then
        echo ""
        echo "--- Compilation Errors ---"
        cargo build --release 2>&1 | grep -A 2 "^error" | head -100
    fi
    
    echo ""
    echo ""
    cd /home/noah/src/reprorusted-python-cli
done

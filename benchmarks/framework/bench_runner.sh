#!/usr/bin/env bash
# Benchmark runner for comparing Python vs Rust CLI performance
# Measures: CPU time, memory usage, binary size

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
RESULTS_DIR="$PROJECT_ROOT/benchmarks/reports"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
WARMUP=3
ITERATIONS=10
MEASURE_MEMORY=true

usage() {
    cat <<EOF
Usage: $0 [OPTIONS] <example_dir>

Benchmark Python vs Rust CLI for a specific example.

Arguments:
    example_dir     Path to example directory (e.g., examples/example_simple)

Options:
    -w, --warmup NUM        Number of warmup iterations (default: 3)
    -i, --iterations NUM    Number of measured iterations (default: 10)
    --no-memory             Skip memory measurement
    -h, --help              Show this help message

Examples:
    $0 examples/example_simple
    $0 -i 20 examples/example_flags
EOF
}

log_info() {
    echo -e "${BLUE}ℹ${NC} $*"
}

log_success() {
    echo -e "${GREEN}✓${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $*"
}

log_error() {
    echo -e "${RED}✗${NC} $*"
}

measure_binary_size() {
    local file="$1"
    if [[ -f "$file" ]]; then
        stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null || echo "0"
    else
        echo "0"
    fi
}

get_python_script() {
    local example_dir="$1"
    # Find the main Python CLI script (not test files)
    find "$example_dir" -maxdepth 1 -name "*.py" ! -name "test_*.py" | head -1
}

get_rust_binary() {
    local example_dir="$1"
    local python_script="$2"
    local script_name
    script_name=$(basename "$python_script" .py)

    # Look for the compiled binary
    if [[ -f "$example_dir/$script_name" ]]; then
        echo "$example_dir/$script_name"
    else
        echo ""
    fi
}

create_wrapper_scripts() {
    local example_dir="$1"
    local python_script="$2"
    local rust_binary="$3"
    local temp_dir="$4"

    # Create Python wrapper
    cat > "$temp_dir/bench_python.sh" <<EOF
#!/usr/bin/env bash
python3 "$python_script" --help >/dev/null 2>&1 || exit 0
EOF
    chmod +x "$temp_dir/bench_python.sh"

    # Create Rust wrapper
    if [[ -n "$rust_binary" ]]; then
        cat > "$temp_dir/bench_rust.sh" <<EOF
#!/usr/bin/env bash
"$rust_binary" --help >/dev/null 2>&1 || exit 0
EOF
        chmod +x "$temp_dir/bench_rust.sh"
    fi
}

run_benchmark() {
    local example_dir="$1"
    local example_name
    example_name=$(basename "$example_dir")

    log_info "Benchmarking $example_name"
    echo ""

    # Find Python script
    local python_script
    python_script=$(get_python_script "$example_dir")
    if [[ -z "$python_script" ]]; then
        log_error "No Python script found in $example_dir"
        return 1
    fi
    log_info "Python script: $(basename "$python_script")"

    # Find Rust binary
    local rust_binary
    rust_binary=$(get_rust_binary "$example_dir" "$python_script")
    if [[ -z "$rust_binary" ]]; then
        log_warning "No Rust binary found. Run 'make compile-all' first."
        log_info "Skipping comparison..."
        return 0
    fi
    log_info "Rust binary: $(basename "$rust_binary")"
    echo ""

    # Measure binary sizes
    local python_size rust_size
    python_size=$(measure_binary_size "$python_script")
    rust_size=$(measure_binary_size "$rust_binary")

    log_info "Binary sizes:"
    printf "  Python: %'d bytes\n" "$python_size"
    printf "  Rust:   %'d bytes\n" "$rust_size"
    echo ""

    # Create temporary directory for wrapper scripts
    local temp_dir
    temp_dir=$(mktemp -d)
    trap "rm -rf '$temp_dir'" EXIT

    create_wrapper_scripts "$example_dir" "$python_script" "$rust_binary" "$temp_dir"

    # Run benchmarks with bashrs
    mkdir -p "$RESULTS_DIR"
    local output_file="$RESULTS_DIR/${example_name}-bench.json"

    log_info "Running benchmark (warmup=$WARMUP, iterations=$ITERATIONS)..."

    local memory_flag=""
    if [[ "$MEASURE_MEMORY" == "true" ]]; then
        memory_flag="--measure-memory"
    fi

    if bashrs bench \
        --warmup "$WARMUP" \
        --iterations "$ITERATIONS" \
        $memory_flag \
        --output "$output_file" \
        "$temp_dir/bench_python.sh" \
        "$temp_dir/bench_rust.sh"; then
        log_success "Benchmark complete"
        log_info "Results saved to: $output_file"
        echo ""

        # Show summary
        if command -v jq >/dev/null 2>&1 && [[ -f "$output_file" ]]; then
            log_info "Summary:"
            jq -r '.benchmarks[] | "  \(if (.script | contains("python")) then "Python" elif (.script | contains("rust")) then "Rust" else .script end): \(.statistics.mean_ms)ms (±\(.statistics.stddev_ms)ms) | Memory: \(.statistics.memory.mean_kb)KB"' "$output_file" 2>/dev/null || true
        fi
    else
        log_error "Benchmark failed"
        return 1
    fi
}

main() {
    local example_dir=""

    while [[ $# -gt 0 ]]; do
        case $1 in
            -w|--warmup)
                WARMUP="$2"
                shift 2
                ;;
            -i|--iterations)
                ITERATIONS="$2"
                shift 2
                ;;
            --no-memory)
                MEASURE_MEMORY=false
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            -*)
                log_error "Unknown option: $1"
                usage
                exit 1
                ;;
            *)
                example_dir="$1"
                shift
                ;;
        esac
    done

    if [[ -z "$example_dir" ]]; then
        log_error "Missing required argument: example_dir"
        usage
        exit 1
    fi

    if [[ ! -d "$example_dir" ]]; then
        log_error "Directory not found: $example_dir"
        exit 1
    fi

    run_benchmark "$example_dir"
}

main "$@"

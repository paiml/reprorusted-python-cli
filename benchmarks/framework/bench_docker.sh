#!/usr/bin/env bash
# Docker benchmark runner - compares Dockerized Python vs Rust binaries
# shellcheck disable=IDEM002

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
RESULTS_DIR="$PROJECT_ROOT/benchmarks/reports"
DOCKER_DIR="$PROJECT_ROOT/docker"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

WARMUP=3
ITERATIONS=10

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

usage() {
    cat <<EOF
Usage: $0 [OPTIONS] <example_name>

Benchmark Dockerized Python vs Rust for a specific example.

Arguments:
    example_name    Example to benchmark (e.g., example_simple)

Options:
    -w, --warmup NUM        Number of warmup iterations (default: 3)
    -i, --iterations NUM    Number of measured iterations (default: 10)
    -h, --help              Show this help message

Examples:
    $0 example_simple
    $0 -i 20 example_flags
EOF
}

build_docker_images() {
    local example_name="$1"
    local example_dir="$PROJECT_ROOT/examples/$example_name"

    log_info "Building Docker images for $example_name..."

    # Build Python image
    if docker build \
        -f "$DOCKER_DIR/$example_name/Dockerfile.python" \
        -t "reprorusted-python:$example_name" \
        . > /dev/null 2>&1; then
        log_success "Built Python image"
    else
        log_error "Failed to build Python image"
        return 1
    fi

    # Build Rust image
    if docker build \
        -f "$DOCKER_DIR/$example_name/Dockerfile.rust" \
        -t "reprorusted-rust:$example_name" \
        . > /dev/null 2>&1; then
        log_success "Built Rust image"
    else
        log_error "Failed to build Rust image"
        return 1
    fi

    echo ""
}

get_image_size() {
    local image="$1"
    docker image inspect "$image" --format='{{.Size}}' 2>/dev/null || echo "0"
}

benchmark_docker_image() {
    local image="$1"
    local name="$2"
    local temp_dir="$3"

    # Create wrapper script for docker run
    cat > "$temp_dir/bench_${name}.sh" <<EOF
#!/usr/bin/env bash
docker run --rm "$image" --help >/dev/null 2>&1 || exit 0
EOF
    chmod +x "$temp_dir/bench_${name}.sh"
}

run_docker_benchmark() {
    local example_name="$1"

    log_info "Benchmarking Docker containers for $example_name"
    echo ""

    # Check if images exist, if not build them
    if ! docker image inspect "reprorusted-python:$example_name" > /dev/null 2>&1 || \
       ! docker image inspect "reprorusted-rust:$example_name" > /dev/null 2>&1; then
        build_docker_images "$example_name" || return 1
    fi

    # Measure image sizes
    local python_size rust_size
    python_size="$(get_image_size "reprorusted-python:$example_name")"
    rust_size="$(get_image_size "reprorusted-rust:$example_name")"

    log_info "Docker image sizes:"
    printf "  Python: %'d bytes (%.2f MB)\n" "$python_size" "$(echo "scale=2; "$python_size" / 1048576" | bc)"
    printf "  Rust:   %'d bytes (%.2f MB)\n" "$rust_size" "$(echo "scale=2; "$rust_size" / 1048576" | bc)"
    echo ""

    # Create temporary directory for wrapper scripts
    local temp_dir
    temp_dir="$(mktemp -d)"
    # shellcheck disable=SEC011
    trap 'rm -rf "${temp_dir:?}"' EXIT

    benchmark_docker_image "reprorusted-python:$example_name" "python" "$temp_dir"
    benchmark_docker_image "reprorusted-rust:$example_name" "rust" "$temp_dir"

    # Run benchmarks
    mkdir -p "$RESULTS_DIR"
    local output_file="$RESULTS_DIR/${example_name}-docker-bench.json"

    log_info "Running Docker benchmark (warmup=$WARMUP, iterations=$ITERATIONS)..."
    log_info "Note: This includes Docker container startup overhead"
    echo ""

    if bashrs bench \
        --warmup "$WARMUP" \
        --iterations "$ITERATIONS" \
        --output "$output_file" \
        "$temp_dir/bench_python.sh" \
        "$temp_dir/bench_rust.sh"; then
        log_success "Docker benchmark complete"
        log_info "Results saved to: $output_file"
        echo ""

        # Add image sizes to JSON
        if command -v jq >/dev/null 2>&1; then
            # Create temp file with sizes
            jq --arg py_size "$python_size" --arg rust_size "$rust_size" \
                '.image_sizes = {python: ("$py_size" | tonumber), rust: ("$rust_size" | tonumber)}' \
                "$output_file" > "$output_file.tmp" && mv "$output_file.tmp" "$output_file"

            log_info "Summary:"
            jq -r '.benchmarks[] | "  \(.name): \(.mean_ms)ms (±\(.std_dev_ms)ms)"' "$output_file" 2>/dev/null || true
            echo ""

            # Calculate size reduction
            local size_reduction
            size_reduction="$(awk "BEGIN {printf \"%.1f\", (1 - $rust_size / $python_size)" * 100}")
            log_info "📦 Image size reduction: ${size_reduction}% (Rust vs Python)"
        fi
    else
        log_error "Docker benchmark failed"
        return 1
    fi
}

main() {
    local example_name=""

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
                example_name="$1"
                shift
                ;;
        esac
    done

    if [[ -z "$example_name" ]]; then
        log_error "Missing required argument: example_name"
        usage
        exit 1
    fi

    run_docker_benchmark "$example_name"
}

main "$@"

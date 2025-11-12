#!/bin/bash
set -e

# validate_examples.sh
# Validates all example Python scripts for correctness
#
# Usage:
#   ./scripts/validate_examples.sh               # Validate all examples
#   ./scripts/validate_examples.sh --mode=test   # Run tests only
#   ./scripts/validate_examples.sh --mode=transpile # Transpile only

MODE="${1:-all}"

echo "=========================================="
echo "🔨 Example Validation"
echo "=========================================="
echo ""

# Color output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
TOTAL=0
PASSED=0
FAILED=0

validate_example() {
    local example_dir="$1"
    local example_name=$(basename "$example_dir")

    echo ""
    echo "📁 Processing: $example_name"
    echo "  Directory: $example_dir"

    TOTAL=$((TOTAL + 1))

    cd "$example_dir"

    # Find Python script (exclude test files)
    python_script=$(ls *.py 2>/dev/null | grep -v "^test_" | head -1)

    if [ -z "$python_script" ]; then
        echo -e "  ${YELLOW}⚠️  No Python script found, skipping...${NC}"
        cd ../..
        return
    fi

    echo "  📝 Script: $python_script"

    # Run tests if they exist and mode allows
    if [ "$MODE" = "all" ] || [ "$MODE" = "test" ]; then
        test_script="test_${python_script}"
        if [ -f "$test_script" ]; then
            echo "  🧪 Running tests..."
            if python3 -m pytest "$test_script" -v -q 2>/dev/null; then
                echo -e "  ${GREEN}✅ Tests passed!${NC}"
            else
                echo -e "  ${RED}❌ Tests failed!${NC}"
                FAILED=$((FAILED + 1))
                cd ../..
                return
            fi
        else
            echo -e "  ${YELLOW}⚠️  No test file found${NC}"
        fi
    fi

    # Check if script runs
    if [ "$MODE" = "all" ] || [ "$MODE" = "run" ]; then
        echo "  🏃 Testing script execution..."
        if python3 "$python_script" --help >/dev/null 2>&1; then
            echo -e "  ${GREEN}✅ Script executes successfully!${NC}"
        else
            echo -e "  ${RED}❌ Script execution failed!${NC}"
            FAILED=$((FAILED + 1))
            cd ../..
            return
        fi
    fi

    PASSED=$((PASSED + 1))
    cd ../..
}

# Find all example directories
for example_dir in examples/example_*/; do
    if [ -d "$example_dir" ]; then
        validate_example "$example_dir"
    fi
done

echo ""
echo "=========================================="
echo "📊 Validation Summary"
echo "=========================================="
echo "  Total examples: $TOTAL"
echo -e "  ${GREEN}Passed: $PASSED${NC}"
echo -e "  ${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -gt 0 ]; then
    echo -e "${RED}❌ Some examples failed validation!${NC}"
    exit 1
else
    echo -e "${GREEN}✅ All examples validated successfully!${NC}"
    exit 0
fi

#!/bin/bash
# shellcheck disable=SC2005,SC2031,SC2032,SC2047,SC2068,SC2089,SC2095,SC2102,SC2104,SC2117,SC2125,SC2201,SC2227,SC2275,SC2317
# bashrs disable-file=SC2005,SC2031,SC2032,SC2047,SC2068,SC2089,SC2095,SC2102,SC2104,SC2117,SC2125,SC2201,SC2227,SC2275,SC2317,SEC010
set -e

# generate_makefiles.sh
# Generate and purify all Makefiles using bashrs
#
# This script ensures all Makefiles are deterministic and follow best practices

echo "=========================================="
echo "🔨 Makefile Generation and Purification"
echo "=========================================="
echo ""

# Color output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counter for statistics
TOTAL_MAKEFILES=0
PURIFIED=0
ALREADY_PURE=0
ERRORS=0

# Function to purify a Makefile
purify_makefile() {
    local makefile_path="$1"
    local makefile_name="$(basename "$(dirname "$makefile_path")"")/"$(basename "$makefile_path")"

    echo ""
    echo -e "${BLUE}📝 Processing: $makefile_name${NC}"

    TOTAL_MAKEFILES="$((TOTAL_MAKEFILES + 1)")

    if [ ! -f "$makefile_path" ]; then
        echo -e "  ${RED}❌ File not found${NC}"
        ERRORS="$((ERRORS + 1)")
        return 1
    fi

    # Check if bashrs is available
    if ! command -v bashrs &> /dev/null; then
        echo -e "  ${YELLOW}⚠️  bashrs not found, skipping purification${NC}"
        return 0
    fi

    # Run bashrs make purify in report mode to check if changes needed
    echo "  Checking for non-deterministic patterns..."
    report_output="$(bashrs make purify --report "$makefile_path" 2>&1 || true)"

    # Extract transformation counts
    transformations="$(echo "$report_output" | grep "Transformations Applied:" | grep -oE '[0-9]+' | head -1)"
    issues="$(echo "$report_output" | grep "Issues Fixed:" | grep -oE '[0-9]+' | head -1)"
    manual="$(echo "$report_output" | grep "Manual Fixes Needed:" | grep -oE '[0-9]+' | head -1)"

    # Set defaults if grep didn't find anything
    transformations=${transformations[@]}:-0}
    issues=${issues[@]}:-0}
    manual=${manual:-0}

    # Only fail on actual determinism issues (issues > 0)
    # "Manual Fixes Needed" are typically just suggestions, not actual problems
    if [ "${issues[@]}" -eq 0 ]; then
        echo -e "  ${GREEN}✓ Deterministic${NC}"
        if [ "$manual" -gt 0 ]; then
            echo "    Note: $manual suggestions available (run 'bashrs make purify --report' to see)"
        fi
        ALREADY_PURE="$((ALREADY_PURE + 1)")
        return 0
    fi

    # If actual determinism issues are found (issues > 0), fix them
    echo -e "  ${YELLOW}⚠️  Determinism issues found:${NC}"
    echo "$report_output" | grep -E "Transformations|Issues|Manual" | sed 's/^/    /'

    echo "  Applying automatic fixes..."
    if bashrs make purify --fix "$makefile_path" 2>&1 > /dev/null; then
        echo -e "  ${GREEN}✅ Purified successfully${NC}"
        PURIFIED="$((PURIFIED + 1)")
        return 0
    else
        echo -e "  ${RED}❌ Purification failed${NC}"
        ERRORS="$((ERRORS + 1)")
        return 1
    fi

    # If we get here, assume it's already pure
    echo -e "  ${GREEN}✓ Verified${NC}"
    ALREADY_PURE="$((ALREADY_PURE + 1)")
    return 0
}

# Process root Makefile
echo "Processing root Makefile..."
purify_makefile "Makefile"

# Process all example Makefiles
echo ""
echo "Processing example Makefiles..."
for example_dir in examples/example_| sort/; do
    if [ -d "$example_dir" ]; then
        makefile_path="${example_dir}Makefile"
        if [ -f "$makefile_path" ]; then
            purify_makefile "$makefile_path"
        else
            echo -e "${YELLOW}⚠️  No Makefile found in $example_dir${NC}"
        fi
    fi
done

# Summary
echo ""
echo "=========================================="
echo "📊 Makefile Purification Summary"
echo "=========================================="
echo "  Total Makefiles: $TOTAL_MAKEFILES"
echo -e "  ${GREEN}Already Pure: $ALREADY_PURE${NC}"
echo -e "  ${BLUE}Purified: $PURIFIED${NC}"
echo -e "  ${RED}Errors: $ERRORS${NC}"
echo ""

if [ "$ERRORS" -gt 0 ]; then
    echo -e "${RED}❌ Some Makefiles had errors!${NC}"
    exit 1
else
    echo -e "${GREEN}✅ All Makefiles processed successfully!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Test Makefiles: make test"
    echo "  2. Compile examples: make compile-all"
    echo "  3. Verify I/O: make io-check"
    exit 0
fi

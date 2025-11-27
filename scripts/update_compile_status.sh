#!/bin/bash
# shellcheck disable=SC2006,SC2031,SC2032,SC2036,SC2046,SC2047,SC2095,SC2099,SC2161,SC2164,SC2204,SC2233
# bashrs disable-file=SC2006,SC2031,SC2032,SC2036,SC2046,SC2047,SC2095,SC2099,SC2161,SC2164,SC2204,SC2233,SEC010,DET002
# Update compile status in README.md
set -e

cd "$(dirname "$0")/.."

echo "🔄 Running compile status check..."

PASS=0
FAIL=0
TOTAL=0
TRANSPILED=0

# Count and test
for dir in examples/example_*/; do
    name=$(basename "$dir")
    TOTAL=$((TOTAL + 1))

    if [ -f "$dir/Cargo.toml" ]; then
        TRANSPILED=$((TRANSPILED + 1))
        if (cd "$dir" && cargo build --quiet 2>/dev/null); then
            PASS=$((PASS + 1))
            echo "✅ $name"
        else
            FAIL=$((FAIL + 1))
            echo "❌ $name"
        fi
    else
        echo "-- $name (not transpiled)"
    fi
done

PERCENT=$((PASS * 100 / TRANSPILED))
DATE=$(date +%Y-%m-%d)

echo ""
echo "📊 Results: $PASS/$TRANSPILED compile ($PERCENT%) | $TOTAL total"

# Update README
sed -i "s/\*\*Latest Testing\*\*:.*/\*\*Latest Testing\*\*: depyler v3.21.0 trunk ($DATE) - \*\*$PASS\/$TRANSPILED COMPILING ($PERCENT%)\*\* | $TOTAL total examples 🎉/" README.md

# Update Progress section
sed -i "s/- \*\*Total Examples\*\*:.*/- \*\*Total Examples\*\*: $TOTAL (expanded from 13 with EXTREME TDD)/" README.md
sed -i "s/- \*\*Transpiled\*\*:.*/- \*\*Transpiled\*\*: $TRANSPILED\/$TOTAL (\*\*$((TRANSPILED * 100 / TOTAL))%\*\*) - Have Cargo.toml/" README.md
sed -i "s/- \*\*Compiling\*\*:.*/- \*\*Compiling\*\*: $PASS\/$TRANSPILED (\*\*$PERCENT%\*\*) - Pass \`cargo build\`/" README.md

echo "✅ README.md updated"

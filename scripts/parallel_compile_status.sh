#!/bin/bash
# shellcheck disable=SC2006,SC2031,SC2032,SC2036,SC2046,SC2047,SC2089,SC2095,SC2097,SC2099,SC2154,SC2161,SC2164,SC2204,SC2227,SC2233
# bashrs disable-file=SC2006,SC2031,SC2032,SC2036,SC2046,SC2047,SC2089,SC2095,SC2097,SC2099,SC2154,SC2161,SC2164,SC2204,SC2227,SC2233,SEC010,SEC018,DET002
# Parallel compile status - 8x faster with xargs -P8
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

echo "🔄 Parallel transpile + compile..."

# Parallel transpile untranspiled examples
find examples/example_*/ -maxdepth 1 -name "*_tool.py" ! -name "test_*" -print0 2>/dev/null | \
  xargs -0 -P8 -I{} bash -c '
    dir=$(dirname "$1")
    if [ ! -f "$dir/Cargo.toml" ]; then
      mkdir -p "$dir/src"
      if depyler transpile "$1" -o "$dir/src/main.rs" 2>/dev/null; then
        [ -f "$dir/src/Cargo.toml" ] && mv "$dir/src/Cargo.toml" "$dir/"
        [ -f "$dir/Cargo.toml" ] && sed -i "s|main.rs|src/main.rs|" "$dir/Cargo.toml"
      fi
    fi
  ' _ {}

# Parallel compile
mapfile -t RESULTS < <(find examples/example_*/Cargo.toml -print0 2>/dev/null | \
  xargs -0 -P8 -I{} bash -c '
    dir=$(dirname "$1")
    name=$(basename "$dir")
    if (cd "$dir" && cargo build --quiet 2>/dev/null); then
      echo "✅ $name"
    else
      echo "❌ $name"
    fi
  ' _ {})

PASS=$(printf '%s\n' "${RESULTS[@]}" | grep -c "✅" || true)
TOTAL=$(find examples/example_*/ -maxdepth 0 -type d 2>/dev/null | wc -l)
TRANSPILED=$(find examples/example_*/Cargo.toml 2>/dev/null | wc -l)

if [ "$TRANSPILED" -gt 0 ]; then
  PERCENT=$((PASS * 100 / TRANSPILED))
else
  PERCENT=0
fi

DATE=$(date +%Y-%m-%d)

printf '%s\n' "${RESULTS[@]}" | tail -20
echo ""
echo "📊 Results: $PASS/$TRANSPILED compile ($PERCENT%) | $TOTAL total"

# Update README
sed -i "s|\*\*Latest Testing\*\*:.*|\*\*Latest Testing\*\*: depyler v3.21.0 trunk ($DATE) - \*\*$PASS/$TRANSPILED COMPILING ($PERCENT%)\*\* \| $TOTAL total examples 🎉|" README.md
sed -i "s|- \*\*Total Examples\*\*:.*|- \*\*Total Examples\*\*: $TOTAL (expanded from 13 with EXTREME TDD)|" README.md
sed -i "s|- \*\*Transpiled\*\*:.*|- \*\*Transpiled\*\*: $TRANSPILED/$TOTAL (\*\*$((TRANSPILED * 100 / TOTAL))%\*\*) - Have Cargo.toml|" README.md
sed -i "s|- \*\*Compiling\*\*:.*|- \*\*Compiling\*\*: $PASS/$TRANSPILED (\*\*$PERCENT%\*\*) - Pass \`cargo build\`|" README.md

echo "✅ README.md updated"

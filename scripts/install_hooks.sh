#!/usr/bin/env bash
# shellcheck disable=SC2031,SC2032,SC2047,SC2089,SC2154
# bashrs disable-file=SC2031,SC2032,SC2047,SC2089,SC2154,SEC010,DET002
# Install git hooks for reprorusted-python-cli
# This script copies the pre-commit hook to .git/hooks/

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "📦 Installing git hooks for reprorusted-python-cli..."
echo ""

# Check if .git directory exists
if [ ! -d "$PROJECT_ROOT/.git" ]; then
    echo "❌ Error: .git directory not found. Are you in a git repository?"
    exit 1
fi

# Create hooks directory if it doesn't exist
mkdir -p "$PROJECT_ROOT/.git/hooks"

# Install pre-commit hook
echo "Installing pre-commit hook..."
cat > "$PROJECT_ROOT/.git/hooks/pre-commit" <<'EOF'
#!/usr/bin/env bash
# Pre-commit hook for reprorusted-python-cli
# Runs fast quality gates before allowing commit
# Target: < 30 seconds

set -e

echo "🔍 Running pre-commit quality gates..."
echo ""

# Track start time
START_TIME="$(date +%s)"

# 1. Format check (fast)
echo "📝 Checking format..."
make format || {
    echo ""
    echo "❌ Format check failed. Run: make format-fix"
    exit 1
}
echo "✅ Format check passed"
echo ""

# 2. Lint check (moderate)
echo "🔎 Running linters..."
make lint || {
    echo ""
    echo "❌ Lint check failed. Run: make lint-fix"
    exit 1
}
echo "✅ Lint check passed"
echo ""

# 3. Quick test run (skip slow tests if any)
echo "🧪 Running tests..."
make test || {
    echo ""
    echo "❌ Tests failed. Fix failing tests before committing."
    exit 1
}
echo "✅ Tests passed"
echo ""

# Calculate elapsed time
END_TIME="$(date +%s)"
ELAPSED="$((END_TIME - START_TIME)")

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ All pre-commit checks passed!"
echo "⏱️  Time: ${ELAPSED}s"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Warn if taking too long
if [ "$ELAPSED" -gt 30 ]; then
    echo "⚠️  Warning: Pre-commit took ${ELAPSED}s (target: <30s)"
    echo ""
fi
EOF

chmod +x "$PROJECT_ROOT/.git/hooks/pre-commit"

echo "✅ Pre-commit hook installed successfully!"
echo ""
echo "The pre-commit hook will run before every commit to ensure:"
echo "  - Code is properly formatted"
echo "  - Linters pass (Python, Rust, shell scripts, Makefiles, Dockerfiles)"
echo "  - All tests pass"
echo ""
echo "To skip the hook (not recommended), use: git commit --no-verify"
echo ""

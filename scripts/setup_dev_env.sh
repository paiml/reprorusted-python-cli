#!/bin/bash
set -e

# setup_dev_env.sh
# Setup development environment for reprorusted-python-cli
#
# This script installs all necessary dependencies and tools

echo "=========================================="
echo "🔧 Development Environment Setup"
echo "=========================================="
echo ""

# Color output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check Python version
echo "📋 Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION found"
else
    echo -e "${RED}✗${NC} Python 3 not found. Please install Python 3.11+"
    exit 1
fi

# Check Rust
echo ""
echo "📋 Checking Rust..."
if command -v rustc &> /dev/null; then
    RUST_VERSION=$(rustc --version | awk '{print $2}')
    echo -e "${GREEN}✓${NC} Rust $RUST_VERSION found"
else
    echo -e "${YELLOW}⚠${NC} Rust not found. Installing..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source "$HOME/.cargo/env"
fi

# Check uv
echo ""
echo "📋 Checking uv..."
if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✓${NC} uv $UV_VERSION found"
else
    echo -e "${YELLOW}⚠${NC} uv not found. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Install Python dependencies with uv
echo ""
echo "📦 Installing Python dependencies..."
if [ -f "pyproject.toml" ]; then
    uv sync
    echo -e "${GREEN}✓${NC} Python dependencies installed"
else
    echo -e "${RED}✗${NC} pyproject.toml not found. Run from repository root."
    exit 1
fi

# Check for depyler
echo ""
echo "📋 Checking depyler..."
if command -v depyler &> /dev/null; then
    DEPYLER_VERSION=$(depyler --version 2>&1 | head -1)
    echo -e "${GREEN}✓${NC} $DEPYLER_VERSION found"
else
    echo -e "${YELLOW}⚠${NC} depyler not found"
    echo "   Install from: https://github.com/paiml/depyler"
    echo "   Or: cargo install --path ../depyler"
fi

# Check for bashrs
echo ""
echo "📋 Checking bashrs..."
if command -v bashrs &> /dev/null; then
    BASHRS_VERSION=$(bashrs --version 2>&1 | head -1)
    echo -e "${GREEN}✓${NC} $BASHRS_VERSION found"
else
    echo -e "${YELLOW}⚠${NC} bashrs not found"
    echo "   Install from: https://github.com/paiml/bashrs"
    echo "   Or: cargo install --path ../bashrs"
fi

# Check for pmat
echo ""
echo "📋 Checking pmat..."
if command -v pmat &> /dev/null; then
    PMAT_VERSION=$(pmat --version 2>&1 | head -1)
    echo -e "${GREEN}✓${NC} $PMAT_VERSION found"
else
    echo -e "${YELLOW}⚠${NC} pmat not found"
    echo "   Install: cargo install pmat"
fi

# Build Rust workspace
echo ""
echo "🔨 Building Rust workspace..."
cargo build
echo -e "${GREEN}✓${NC} Rust workspace built"

echo ""
echo "=========================================="
echo "✅ Development Environment Ready!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Run examples: cd examples/example_simple && python3 trivial_cli.py --help"
echo "  2. Run tests: uv run pytest test_trivial_cli.py -v"
echo "  3. Validate all: ./scripts/validate_examples.sh"
echo "  4. See README.md for full documentation"
echo ""

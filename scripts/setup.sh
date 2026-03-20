#!/usr/bin/env bash
set -e

echo ""
echo "  context-pilot setup"
echo "  ────────────────────"
echo ""

# ── Node / pnpm ──────────────────────────────────────────────────────────────
if ! command -v node &>/dev/null; then
  echo "  ✗ Node.js not found. Install from https://nodejs.org (>=20)"
  exit 1
fi

if ! command -v pnpm &>/dev/null; then
  echo "  Installing pnpm..."
  npm install -g pnpm
fi

echo "  Installing Node dependencies..."
pnpm install

echo "  Building TypeScript..."
pnpm build

# ── Python ───────────────────────────────────────────────────────────────────
PYTHON=python3
if ! command -v python3 &>/dev/null; then
  PYTHON=python
fi

if ! command -v $PYTHON &>/dev/null; then
  echo "  ✗ Python 3.11+ not found. Install from https://python.org"
  exit 1
fi

PY_VERSION=$($PYTHON -c "import sys; print(sys.version_info.minor)")
if [ "$PY_VERSION" -lt 11 ]; then
  echo "  ✗ Python 3.11+ required (found 3.$PY_VERSION)"
  exit 1
fi

ENGINE_DIR="packages/embedding-engine"

echo "  Creating Python virtual environment..."
$PYTHON -m venv "$ENGINE_DIR/.venv"

if [ -f "$ENGINE_DIR/.venv/bin/activate" ]; then
  source "$ENGINE_DIR/.venv/bin/activate"
else
  source "$ENGINE_DIR/.venv/Scripts/activate"  # Windows
fi

echo "  Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r "$ENGINE_DIR/requirements.txt"

echo ""
echo "  ✓ Setup complete"
echo ""
echo "  Next steps:"
echo "    cd your-project"
echo "    context-pilot init"
echo "    context-pilot index"
echo "    context-pilot serve --watch"
echo ""
echo "  Add to Claude Code:"
echo "    claude mcp add context-pilot -- context-pilot serve --project ."
echo ""

#!/usr/bin/env bash
# =================================================================
#  NRC Protein Folding — Virtual Environment Setup Script
# =================================================================
#  Creates a local Python virtual environment for running
#  protein folding scripts and NRC math modules
#  without modifying your system Python.
#
#  USAGE:
#    chmod +x setup_venv.sh
#    ./setup_venv.sh
#
#  PREREQUISITES:
#    Pop!_OS / Ubuntu / Debian:  sudo apt install python3.12-venv
#    macOS: (included with Python from Homebrew or python.org)
#    Windows: (included with Python from python.org)
# =================================================================

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/.venv"

echo "═══════════════════════════════════════════════════════════"
echo "  NRC Protein Folding — Virtual Environment Setup"
echo "═══════════════════════════════════════════════════════════"

if [ -d "${VENV_DIR}" ]; then
    echo "[!] .venv already exists. Delete it first: rm -rf .venv"
    exit 1
fi

echo "[1/3] Creating virtual environment..."
python3 -m venv "${VENV_DIR}"

echo "[2/3] Installing dependencies..."
source "${VENV_DIR}/bin/activate"
pip install --upgrade pip
pip install torch numpy mpmath sympy biopython pyyaml

echo "[3/3] Verifying..."
python -c "
import torch, mpmath
from src.nrc_math.phi import PHI_FLOAT
print(f'  PyTorch: {torch.__version__}')
print(f'  φ = {PHI_FLOAT:.15f}')
print('  All imports OK!')
"

echo ""
echo "  Activate with: source .venv/bin/activate"
echo "  Run tests:     python -m pytest tests/ -v"
echo "═══════════════════════════════════════════════════════════"

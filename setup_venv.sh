#!/usr/bin/env bash
# ===========================================================
#  nrc_bio — Virtual Environment Setup
# ===========================================================
#  Creates an isolated .venv, installs the nrc core library
#  from GitHub, installs PyTorch (CPU) + BioPython, and
#  then installs the nrc_bio package in editable mode.
#
#  PREREQUISITE (one-time, Pop!_OS / Ubuntu / Debian):
#    sudo apt install python3.12-venv
#
#  USAGE:  ./setup_venv.sh
#          source .venv/bin/activate
# ===========================================================

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/.venv"
RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; NC='\033[0m'

echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  nrc_bio Library — Virtual Environment Setup${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"

# ── Prerequisite check ─────────────────────────────────────
if ! python3 -m venv --help &>/dev/null; then
    echo -e "${RED}[!] python3-venv is not available.${NC}"
    echo "    Run: sudo apt install python3.12-venv"
    exit 1
fi

if [ -d "${VENV_DIR}" ]; then
    echo -e "${RED}[!] .venv already exists. To recreate: rm -rf .venv${NC}"
    exit 1
fi

echo "[1/5] Creating virtual environment at .venv ..."
python3 -m venv "${VENV_DIR}"

echo "[2/5] Upgrading pip ..."
"${VENV_DIR}/bin/pip" install --upgrade pip --quiet

echo "[3/5] Installing nrc core library (from GitHub) ..."
"${VENV_DIR}/bin/pip" install \
    "nrc @ git+https://github.com/Nexus-Resonance-Codex/NRC.git" --quiet

echo "[4/5] Installing PyTorch (CPU) + BioPython + nrc_bio ..."
"${VENV_DIR}/bin/pip" install torch --index-url https://download.pytorch.org/whl/cpu --quiet
"${VENV_DIR}/bin/pip" install -e ".[dev]" --no-deps --quiet
"${VENV_DIR}/bin/pip" install pytest ruff mypy numpy biopython --quiet

echo "[5/5] Verifying installation ..."
"${VENV_DIR}/bin/python" -c "
import nrc, torch
from nrc.math.phi import PHI_FLOAT
from nrc_bio.sequence.parser import sequence_to_mass_array
from nrc_bio.distributed.boinc import generate_boinc_workunits

masses = sequence_to_mass_array('MKTIIALSYIFCLVFA')
wus = generate_boinc_workunits(masses, shard_count=4)
print(f'  nrc version       : {nrc.__version__}')
print(f'  torch version     : {torch.__version__}')
print(f'  Sequence masses   : {masses[:3]} ...')
print(f'  BOINC work units  : {len(wus)} shards generated')
print('  ✓ All imports OK!')
"

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✓ Setup complete!${NC}"
echo ""
echo "  Activate with:   source .venv/bin/activate"
echo "  Run tests:       pytest tests/ -v"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"

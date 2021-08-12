#!/bin/bash
# Creates a "latest" environment from key packages
if [ -z "${1}" ]; then
  echo "Usage: create_base_env.sh [relnum] [base] [python_ver]"
  exit
else
  REL="${1}"
fi
if [ -z "${2}" ]; then
  BASE="pcds"
else
  BASE="${2}"
fi
if [ -z "${3}" ]; then
  PY_VER="3.9"
else
  PY_VER="${3}"
fi
ENVNAME="${BASE}-${REL}"
set -e
source "$(dirname `which conda`)/../etc/profile.d/conda.sh"
ENV_DIR="../envs/${BASE}"
conda create -y --name "${ENVNAME}" python="${PY_VER}" --file "${ENV_DIR}/conda-packages.txt"
conda activate "${ENVNAME}"
pip install -r "${ENV_DIR}/pip-packages.txt"
conda deactivate

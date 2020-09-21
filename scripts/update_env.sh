#!/bin/bash
# Updates the previous environment to a new latest, rather than starting from scratch.
if [ -z "${1}" ]; then
  echo "Usage: update_env.sh [relnum] [base]"
  exit
else
  REL="${1}"
fi
if [ -z "${2}" ]; then
  BASE="pcds"
else
  BASE="${2}"
fi
ENVNAME="${BASE}-${REL}"
set -e
source "$(dirname `which conda`)/../etc/profile.d/conda.sh"
ENV_DIR="../envs/${BASE}"
conda env create --name "${ENVNAME}" --file "${ENV_DIR}/env.yaml"
conda activate "${ENVNAME}"
conda install --file "${ENV_DIR}/conda-packages.txt"
pip install -r "${ENV_DIR}/pip-packages.txt"
conda deactivate

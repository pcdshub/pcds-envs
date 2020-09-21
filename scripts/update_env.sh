#!/bin/bash
# Updates the previous environment to a new latest, rather than starting from scratch.
if [ -z "${1}" ]; then
  echo "Usage: update_env.sh [envname] [base]"
  exit
else
  ENVNAME="${1}"
  BASE="${2}"
fi
set -e
source "$(dirname `which conda`)/../etc/profile.d/conda.sh"
ENV_DIR="../envs/${BASE}"
HASREL=`conda env list | grep "${NAME}"`
if [ -z "${HASREL}" ]; then
  conda env create --name "${ENVNAME}" --file "${ENV_DIR}/env.yaml"
fi
conda activate "${ENVNAME}"
conda install --file "${ENV_DIR}/conda-packages.txt"
pip install -r "${ENV_DIR}/pip-packages.txt"
conda deactivate

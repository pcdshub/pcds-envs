#!/bin/bash
# Updates the previous environment to a new latest, rather than starting from scratch.
if [ -z "${1}" ]; then
  echo "Usage: update_env.sh [envname] [base] [py_ver]"
  exit
else
  ENVNAME="${1}"
fi
if [ -z "${2}" ]; then
  BASE="pcds"
else
  BASE="${2}"
fi
if [ -z "${3}" ]; then
  VER="3.6"
else
  VER="${3}"
fi
set -e
source "$(dirname `which conda`)/../etc/profile.d/conda.sh"
ENV_DIR="../envs/${BASE}"
HASREL=`mamba env list | grep "${NAME}"`
if [ -z "${HASREL}" ]; then
  mamba env create -y --name "${ENVNAME}" --file "${ENV_DIR}/env.yaml"
fi
conda activate "${ENVNAME}"
conda info -a
echo "Installing python version ${VER}"
conda activate base
conda info -a
mamba install -y -n "${ENVNAME}" python="${VER}"
echo "Updating tagged packages"
mamba install -y -n "${ENVNAME}" --file "${ENV_DIR}/conda-packages.txt"
conda activate "${ENVNAME}"
pip install -r "${ENV_DIR}/pip-packages.txt"
conda list
conda deactivate

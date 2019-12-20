#!/bin/bash
# Creates a "latest" environment from key packages
if [ -z $1 ]; then
  echo "Usage: create_base_env.sh [envname] [python_ver]"
  exit
else
  ENVNAME="${1}"
fi
if [ -z $2 ]; then
  PY_VER="3.6"
else
  PY_VER="${2}"
fi
set -e
source "$(dirname `which conda`)/../etc/profile.d/conda.sh"
ENV_DIR="envs/${ENVNAME}"
conda create -y --name $ENVNAME python=$PY_VER --file "${ENV_DIR}/conda-packages.txt"
conda activate $ENVNAME
pip install "${ENV_DIR}/pip-packages.txt"
conda deactivate

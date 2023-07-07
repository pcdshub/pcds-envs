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
set -e
ENVNAME="${BASE}-${REL}"
source "$(dirname "$(which conda)")/../etc/profile.d/conda.sh"
ENV_DIR="../envs/${BASE}"

# Main conda install step
mamba create -y --name "${ENVNAME}" python="${PY_VER}" --file "${ENV_DIR}/conda-packages.txt"
conda activate "${ENVNAME}"

# First extras round to pick up conda stuff
python get_extras.py "${BASE}" > "${ENV_DIR}"/extras_conda.txt
mamba install --file "${ENV_DIR}"/extras_conda.txt

# Main pip install step
pip install -r "${ENV_DIR}"/pip-packages.txt

# Second extras round to pick up pypi stuff
python get_extras.py "${BASE}" > "${ENV_DIR}"/extras_pip.txt
# Looks redundant to force pypi to not "forget" about previous pins
pip install -r "${ENV_DIR}"/pip-packages.txt -r "${ENV_DIR}"/extras_pip.txt

# Environment can opt in to doing special steps at the end
"${ENV_DIR}"/extra-install-steps.sh
./install_activate.sh "${BASE}" "${ENVNAME}"
conda deactivate

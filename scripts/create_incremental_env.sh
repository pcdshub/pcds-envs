#!/bin/bash
# Create a new conda env that follows the updated specs but is as similar
# to the previous environment as possible.
# The previous environment is by default the one present on the master
# branch, but we can create an incremental environment starting at any
# valid git reference.

if [ -z "${1}" ]; then
  echo "Usage: create_incremental_env.sh [relnum] [base] [git_ref]"
else
  REL="${1}"
fi
if [ -z "${2}" ]; then
  BASE="pcds"
else
  BASE="${2}"
fi
if [ -z "${3}" ]; then
  GIT_REF="master"
else
  GIT_REF="${3}"
fi
set -e

ENVNAME="${BASE}-${REL}"
ENV_DIR="../envs/${BASE}"

# Make a temp environment descriptor
TEMP_ENV=".temp_env.yaml"
git show "${GIT_REF}:envs/pcds/env.yaml" > "${TEMP_ENV}"

# Create a copy of the old environment under the new name
mamba env create -n "${ENVNAME}" -f "${TEMP_ENV}"

# Update the copy minimally with our new specs
mamba install -y -n "${ENVNAME}" --file "${ENV_DIR}/conda-packages.txt"
conda activate "${ENVNAME}"
pip install -r "${ENV_DIR}/pip-packages.txt"
${ENV_DIR}/extra-install-steps.sh
./install_activate.sh "${BASE}" "${ENVNAME}"
conda deactivate


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
# shellcheck disable=SC1091
source "$(dirname "$(which conda)")/../etc/profile.d/conda.sh"

# Make a temp environment descriptor
TEMP_ENV=".temp_env.yaml"
git show "${GIT_REF}:${ENV_DIR}/env.yaml" > "${TEMP_ENV}"

# Create a copy of the old environment under the new name
mamba env create -q -n "${ENVNAME}" -f "${TEMP_ENV}"

# Make a temp minimal update list
TEMP_CONDA_UP=".conda_up.txt"
git diff "${GIT_REF}" "${ENV_DIR}/conda-packages.txt" | grep "^+\w" | cut -c 2- > "${TEMP_CONDA_UP}"

# Update the copy minimally with our new specs
mamba install -q -y -n "${ENVNAME}" --file "${TEMP_CONDA_UP}"
conda activate "${ENVNAME}"

# First extras round to pick up conda stuff
python get_extras.py "${BASE}" > "${ENV_DIR}"/extras_conda.txt
mamba install --file "${ENV_DIR}"/extras_conda.txt

# Install from the pinned latest versions in case something wants an update
pip install -r "${ENV_DIR}"/pip-packages.txt

# Second extras round to pick up pypi stuff
python get_extras.py "${BASE}" > "${ENV_DIR}"/extras_pip.txt
# Looks redundant to force pypi to not "forget" about previous pins
pip install -r "${ENV_DIR}"/pip-packages.txt -r "${ENV_DIR}"/extras_pip.txt

# Environment can opt in to doing special steps at the end
"${ENV_DIR}"/extra-install-steps.sh
./install_activate.sh "${BASE}" "${ENVNAME}"
conda deactivate

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

# Make a temp environment descriptor without the pypi reqs
TEMP_CONDA=".temp_env.yaml"
git show "${GIT_REF}:envs/pcds/env.yaml" | grep -v "pip:" | grep -v "      -" > "${TEMP_CONDA}"

# Create a copy of the old environment's conda specs under the new name
mamba env create -q -n "${ENVNAME}" -f "${TEMP_CONDA}"

# Update the copy minimally with our new specs
mamba install -q -y -n "${ENVNAME}" --file "${ENV_DIR}/conda-packages.txt"
conda activate "${ENVNAME}"

# Invert the remove pips thing from earlier to get only the pip deps exactly"
TEMP_PIP=".temp_pip.txt"
git show "${GIT_REF}:envs/pcds/env.yaml" | grep "      -" | cut -c 9- > "${TEMP_PIP}"

# Install exactly the versions we used last time from pip
pip install -r "${TEMP_PIP}"
# Install from the pinned latest versions in case something wants an update
pip install -r "${ENV_DIR}/pip-packages.txt"
"${ENV_DIR}"/extra-install-steps.sh
./install_activate.sh "${BASE}" "${ENVNAME}"
conda deactivate

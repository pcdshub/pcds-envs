#!/bin/bash
if [ -z "${1}" ]; then
  echo "Usage: apply_release.sh [relnum] [base]"
  exit
else
  REL="${1}"
fi
set -e
source "$(dirname `which conda`)/../etc/profile.d/conda.sh"
echo "Updating to latest"
git checkout master
git pull origin master
if [ -z "${2}" ]; then
  BASE="pcds"
  TAG="${REL}"
else
  BASE="${2}"
  TAG="${BASE}-${REL}"
fi
ENV_DIR="../envs/${BASE}"
YAML="${ENV_DIR}/env.yaml"
NAME="${BASE}-${REL}"
echo "Applying release ${NAME}"
echo "Checking for tag ${TAG}"
git fetch origin
git checkout "${TAG}"
echo "Building environment"
mamba env create -n "${NAME}" -f "${YAML}"
./install_activate.sh "${BASE}" "${NAME}"
CONDA_BIN=`dirname $(which conda)`
"${ENV_DIR}"/extra-install-steps.sh
echo "Write-protecting new env"
pushd "${CONDA_BIN}/../envs"
chmod -R a-w ${NAME}
popd
git checkout master
echo "Done"

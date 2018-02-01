#!/bin/bash
set -e
if [ -z "${1}" ]; then
  echo "Usage: apply_release.sh [relnum] [base]"
  exit
else
  REL="${1}"
fi
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
YAML="../${BASE}.yaml"
NAME="${BASE}-${REL}"
echo "Applying release ${NAME}"
echo "Checking for tag ${TAG}"
git fetch origin
git checkout "${TAG}"
echo "Building environment"
conda env create -n "${NAME}" -f "${YAML}"
source activate "${NAME}"
conda install conda-wrappers -y
source deactivate
CONDA_BIN=`dirname $(which conda)`
echo "Write-protecting new env"
pushd "${CONDA_BIN}/../envs"
chmod -R a-w ${NAME}
popd
echo "Setting execute permissions"
pushd "${CONDA_BIN}/../envs/${NAME}/bin/wrappers/conda"
chmod a+x *
popd
git checkout master
echo "Done"

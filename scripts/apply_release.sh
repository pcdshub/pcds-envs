#!/bin/bash
set -e
if [ -z "${1}" ]; then
  echo "Usage: apply_release.sh [relnum] [base]"
  exit
else
  REL="${1}"
fi
if [ -z "${2}" ]; then
  BASE="pcds"
else
  BASE="${2}"
fi
git fetch origin
git checkout "${REL}"
YAML="../${BASE}.yaml"
NAME="${BASE}-${REL}"
conda env create -n "${NAME}" -f "${YAML}"
CONDA_BIN=`dirname $(which conda)`
pushd "${CONDA_BIN}/../envs"
chmod -R a-w ${NAME}
popd

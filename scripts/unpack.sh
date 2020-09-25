#!/bin/bash
# Script to unpack a specific environment into a target directory
ENV="${1}"
DIR="${2}"
PACKS="${3}"

if [ -z "${DIR}" ]; then
  echo "Usage: unpack.sh <ENV> <DIR>"
  echo "Example: unpack.sh pcds-3.3.4 /u1/conda"
  echo "This will install /u1/conda/pcds-3.3.4"
fi

if [ -z "${PACKS}" ]; then
  PACKS="/reg/g/pcds/pyps/conda/packed_envs"
fi

ENV_FILE="${PACKS}/${ENV}.tar.gz"
TARGET="${DIR}/${ENV}"
ACTIVATE="${TARGET}/bin/activate"
DEACTIVATE="${TARGET}/bin/deactivate"

if [ -f "${ENV_FILE}" ]; then
  echo "Creating ${TARGET}"
  mkdir "${TARGET}"
  echo "Untarring ${ENV_FILE} into ${TARGET}"
  tar -xzf "${ENV_FILE}" -C "${TARGET}"
  if [ -f "${ACTIVATE}" ]; then
    echo "Unpacking conda environment"
    source "${ACTIVATE}"
    conda-unpack
    source "${DEACTIVATE}"
    echo "Done!"
  else
    echo "Could not execute ${ACTIVATE}, something went wrong"
    echo "Aborting"
  fi
else
  echo "Could not find ${ENV_FILE}, something went wrong"
  echo "Aborting"
fi

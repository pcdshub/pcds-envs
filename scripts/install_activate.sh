#!/bin/bash
# Add activate/deactivate scripts to a conda environment.
USAGE="Usage: install_activate.sh [base] [dest_env]"
if [ -z "${1}" ]; then
  echo "${USAGE}"
  exit
else
  BASE="${1}"
fi
if [ -z "${2}" ]; then
  echo "${USAGE}"
  exit
else
  DEST="${2}"
fi

ACTIVE_ENV="${CONDA_PREFIX}/envs"
BASE_ENV="${CONDA_PREFIX_1}/envs"
if [ -d "${ACTIVE_ENV}" ]; then
    ENVS_DIR="${ACTIVE_ENV}"
elif [ -d "${BASE_ENV}" ]; then
    ENVS_DIR="${BASE_ENV}"
else
    echo "Could not find envs dir!"
    exit 1
fi
STARTUP_DIR="${ENVS_DIR}/${DEST}/etc/conda"
ACTIVATE_DIR="${STARTUP_DIR}/activate.d"
DEACTIVATE_DIR="${STARTUP_DIR}/deactivate.d"
ENV_DIR = "../envs/${BASE}"

AT_LEAST_ONE=''
if [ -d "${ACTIVATE_DIR}" ]; then
    for script_path in "${ENV_DIR}/*_activate.sh"; do
        AT_LEAST_ONE='1'
        echo "Copying ${script_path} to ${ACTIVATE_DIR}"
        cp ${script_path} ${ACTIVATE_DIR}
    if [ -z "${AT_LEAST_ONE}" ]; then
        echo "No activate scripts copied."
    fi
else
    echo "Could not locate ${ACTIVATE_DIR}"
fi

AT_LEAST_ONE=''
if [ -d "${DEACTIVATE_DIR}" ]; then
    for script_path in "${ENV_DIR}/*_deactivate.sh"; do
        AT_LEAST_ONE='1'
        echo "Copying ${script_path} to ${DEACTIVATE_DIR}"
        cp ${script_path} ${DEACTIVATE_DIR}
    if [ -z "${AT_LEAST_ONE}" ]; then
        echo "No deactivate scripts copied."
    fi
else
    echo "Could not locate ${DEACTIVATE_DIR}"
fi
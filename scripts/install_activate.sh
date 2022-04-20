#!/bin/bash
# Add activate/deactivate scripts to a conda environment.
USAGE="Usage: install_activate.sh [base] [dest_env]"
if [ -z "${1}" ]; then
  echo "${USAGE}"
  exit 1
else
  BASE="${1}"
fi
if [ -z "${2}" ]; then
  echo "${USAGE}"
  exit 1
else
  DEST="${2}"
fi

CONDA_EXE="$(which conda)"
if [ -z "${CONDA_EXE}" ]; then
  echo "No conda environment is active!"
  exit 1
fi
CONDA_LOCATION="$(dirname "${CONDA_EXE}")"
# If base env or no env is active
ENVS_DIR_1="${CONDA_LOCATION}/../envs"
# If any other env is active
ENVS_DIR_2="${CONDA_LOCATION}/../../../envs"
if [ -d "${ENVS_DIR_1}" ]; then
  ENVS_DIR="${ENVS_DIR_1}"
elif [ -d "${ENVS_DIR_2}" ]; then
  ENVS_DIR="${ENVS_DIR_2}"
else
  echo "Could not find envs dir!"
  echo "Neither ${ENVS_DIR_1} or ${ENVS_DIR_2} exists!"
  exit 1
fi
ENVS_DIR="$(readlink -f "${ENVS_DIR}")"

STARTUP_DIR="${ENVS_DIR}/${DEST}/etc/conda"
ACTIVATE_DIR="${STARTUP_DIR}/activate.d"
DEACTIVATE_DIR="${STARTUP_DIR}/deactivate.d"
ENV_CONFIG_DIR="../envs/${BASE}"

AT_LEAST_ONE=''
if [ -d "${ACTIVATE_DIR}" ]; then
  for script_path in "${ENV_CONFIG_DIR}"/*_activate.sh; do
    AT_LEAST_ONE='1'
    echo "Copying ${script_path} to ${ACTIVATE_DIR}"
    cp "${script_path}" "${ACTIVATE_DIR}"
  done
  if [ -z "${AT_LEAST_ONE}" ]; then
    echo "No activate scripts copied."
  fi
else
  echo "Could not locate ${ACTIVATE_DIR}"
fi

AT_LEAST_ONE=''
if [ -d "${DEACTIVATE_DIR}" ]; then
  for script_path in "${ENV_CONFIG_DIR}"/*_deactivate.sh; do
    AT_LEAST_ONE='1'
    echo "Copying ${script_path} to ${DEACTIVATE_DIR}"
    cp "${script_path}" "${DEACTIVATE_DIR}"
  done
  if [ -z "${AT_LEAST_ONE}" ]; then
    echo "No deactivate scripts copied."
  fi
else
  echo "Could not locate ${DEACTIVATE_DIR}"
fi


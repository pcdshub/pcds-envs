#!/bin/bash
# Identify which conda packages can be installed with a
# particular python version and which cannot.
if [ -z "${1}" ]; then
  echo "Usage: check_py_compat.sh [base] [python_ver]"
  exit
else
  BASE="${1}"
fi
if [ -z "${2}" ]; then
  PY_VER="3.10"
else
  PY_VER="${2}"
fi
EXIT_CODE=0
while read -r line;
do
  if [[ "${line}" == "#"* ]]; then
    continue
  fi
  if conda create --dry-run --name debug_test python="${PY_VER}" "${line}" --file "../envs/${BASE}/security-packages.txt" > /dev/null 2>&1; then
    echo "Found working package ${line}"
  else
    echo "Found uninstallable package ${line}"
    EXIT_CODE=1
  fi
done < "../envs/${BASE}/conda-packages.txt"
exit $EXIT_CODE

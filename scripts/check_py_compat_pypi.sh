#!/bin/bash
# Identify which pypi packages can be installed in your current python environment
# from on your environment specifications
if [ -z "${1}" ]; then
  echo "Usage: check_py_compat_pypi.sh [base]"
  exit
else
  BASE="${1}"
fi

EXIT_CODE=0
while read -r line;
do
  if [[ "${line}" == "#"* ]]; then
    continue
  fi
  if pip install --dry-run "${line}" > /dev/null 2>&1; then
    echo "Found working package ${line}"
  else
    echo "Found uninstallable package ${line}"
    EXIT_CODE=1
  fi
done < "../envs/${BASE}/pip-packages.txt"
exit $EXIT_CODE

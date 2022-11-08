#! /usr/bin/env bash
set -e

# Check for basic entry point failures
hutch-python --help
lightpath --help
pmgrLauncher.sh --help
pydm --help
pytmc --help
typhos --help
whatrecord --help

# Check for inclusions in PYQTDESIGNERPATH
for package in pydm; do
  if [[ "${PYQTDESIGNERPATH}" != *"${package}"* ]]; then
    echo "Did not find ${package} in PYQTDESIGNERPATH=${PYQTDESIGNERPATH}"
    exit 1
  fi
done

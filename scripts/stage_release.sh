#!/bin/bash
# Runs create_base_env if needed, then pushes a new yaml
set -e
if [ -z "${1}" ]; then
  echo "Usage: stage_release.sh [relnum] [base]"
  exit
else
  REL="${1}"
fi
if [ -z "${2}" ]; then
  BASE="pcds"
else
  BASE="${2}"
fi
BRANCH="rel-${REL}"
NAME="${BASE}-${REL}"
HASBRANCH=`git branch | grep "${BRANCH}"`
HASREL=`conda env | grep "${NAME}"`
if [ -z "${HASBRANCH}" ]; then
  git checkout -b "${BRANCH}"
else
  git checkout "${BRANCH}"
fi
if [ -z "${HASREL}" ]; then
  ./make_base_env.sh "${NAME}"
fi
conda env export -n "${NAME}" -f "../${BASE}.yaml"
git add "${BASE}.yaml"
git commit -m "ENH: updated ${BASE} to ${REL}"
git push origin "${BRANCH}"

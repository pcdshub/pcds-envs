#!/bin/bash
# Runs create_base_env if needed, then pushes a new yaml
if [ -z "${1}" ]; then
  echo "Usage: stage_release.sh [relnum] [base] [git_ref]"
  exit
else
  REL="${1}"
fi
if [ -z "${2}" ]; then
  BASE="pcds"
else
  BASE="${2}"
fi
if [ -n "${3}" ]; then
  GIT_REF="${3}"
fi
BRANCH="rel-${REL}"
NAME="${BASE}-${REL}"
echo "Staging environment ${NAME} for release"
HASBRANCH=`git branch | grep "${BRANCH}"`
HASREL=`mamba env list | grep "${NAME}"`
set -e
if [ -z "${HASBRANCH}" ]; then
  echo "Creating branch ${BRANCH}"
  git checkout -b "${BRANCH}"
else
  echo "Switching to branch ${BRANCH}"
  git checkout "${BRANCH}"
fi
if [ -z "${HASREL}" ]; then
  echo "Automatically updating ${BASE} environment specs"
  python update_tags.py "${BASE}"
  echo "Building environment ${NAME}"
  if [ -z "${GIT_REF}" ]; then
    ./create_base_env.sh "${REL}" "${BASE}"
  else
    ./create_incremental_env.sh "${REL}" "${BASE}" "${GIT_REF}"
  fi
else
  echo "Using existing environment ${NAME}"
fi
CONDA_TAGS="../envs/${BASE}/conda-packages.txt"
PIP_TAGS="../envs/${BASE}/pip-packages.txt"

echo "Exporting yaml file"
YAML="../envs/${BASE}/env.yaml"
mamba env export -n "${NAME}" -f "${YAML}"
echo "Committing and pushing"
git add "${YAML}"
git add "${CONDA_TAGS}"
git add "${PIP_TAGS}"
git commit -m "ENH: updated ${BASE} to ${REL}"
git push origin "${BRANCH}"
if [ -x "$(command -v conda-pack)" ]; then
  PACKDIR="${HOME}/pcds-envs-packs"
  PACKPATH="${PACKDIR}/${NAME}.tar.gz"
  echo "Packing env into ${PACKPATH}"
  mkdir -p "${PACKDIR}"
  conda-pack -n "${NAME}" -o "${PACKPATH}"
else
  echo "conda-pack is not installed, skipping step"
fi
echo "Done"

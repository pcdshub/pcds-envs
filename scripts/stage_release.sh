#!/bin/bash
# Runs create_base_env if needed, then pushes a new yaml
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
echo "Staging environment ${NAME} for release"
HASBRANCH=`git branch | grep "${BRANCH}"`
HASREL=`conda env list | grep "${NAME}"`
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
  ./create_base_env.sh "${REL}" "${BASE}"
else
  echo "Using existing environment ${NAME}"
fi
echo "Exporting yaml file"
YAML="../envs/${BASE}/env.yaml"
conda env export -n "${NAME}" -f "${YAML}" --no-builds
echo "Committing and pushing"
git add "${YAML}"
git commit -m "ENH: updated ${BASE} to ${REL}"
git push origin "${BRANCH}"
if [ -x "$(command -v conda-pack)" ]; then
  PACKDIR="${HOME}/pcds-envs-packs"
  PACKPATH="${PACKDIR}/${NAME}.tar.gz"
  echo "Packing env into ${PACKPATH}"
  mkdir -p "${PACKDIR}"
  conda-pack -n "${NAME}" -o "${PACKPATH}"
fi
echo "Done"

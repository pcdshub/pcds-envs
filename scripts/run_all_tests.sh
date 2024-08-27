ERROR=0
ERR_PKGS=""
WARN_PKGS=""
RETRIES=5

for dir in tests/*
do
  retries=$RETRIES
  echo "Running tests for ${dir}"
  pushd "${dir}"
  # Check on the repo for debugging purposes
  git status
  git rev-parse HEAD
  # Try a few times. Allow pass with a warning for race conditions in tests.
  while [ $retries -gt 0 ]; do
    if [ -f "run_tests.py" ]; then
      timeout 10m python run_tests.py
    else
      timeout 10m python -m pytest
    fi
    # Accumulate error codes, else the loop eats them
    retcode=$?
    if [ "${retcode}" -eq "0" ]; then
      break
    else
      if [ "${retcode}" -eq "124" ]; then
        echo "Test timed out after 10 minutes, killed with SIGTERM"
      elif [ "${retcode}" -eq "137" ]; then
        echo "Test timed out after 10 minutes, killed with SIGKILL"
      fi
      (( retries -= 1 ))
    fi
  done
  if [ "${retcode}" -ne "0" ]; then
    ERR_PKGS="${ERR_PKGS}\n${dir}"
    color="31" # Red
  elif [ "${retries}" -lt "${RETRIES}" ]; then
    WARN_PKGS="${WARN_PKGS}\n${dir}"
    color="33" # Yellow
  else
    color="32" # Green
  fi
  echo -e "\033[0;${color}mTest for ${dir} finished with exit code ${retcode}\033[0m"
  (( ERROR += $retcode ))
  popd
done

echo "summary_start"

# If ERROR is nonzero, at least one of the run_test.py calls failed
if [ -n "${ERR_PKGS}" ]; then
  echo -e "\033[0;31mThe following packages failed all retries:${ERR_PKGS}\033[0m"
else
  echo -e "\033[0;32mAll package tests passed!\033[0m"
fi
if [ -n "${WARN_PKGS}" ]; then
  echo -e "\033[0;33mThe following packages had race conditions, but passed at least once:${WARN_PKGS}\033[0m"
else
  echo -e "\033[0;32mNo packages had race conditions!\033[0m"
fi

echo "summary_end"

# Do the environment's extra tests if they exist
if [ -n "${1}" ]; then
  EXTRA_TESTS="$(readlink -f $(dirname ${BASH_SOURCE[0]}))/../envs/${1}/extra-tests.sh"
  if [ -f "${EXTRA_TESTS}" ]; then
    echo "Running ${EXTRA_TESTS}"
    cat "${EXTRA_TESTS}"
    bash "${EXTRA_TESTS}"
    retcode=$?
    if [ "${retcode}" -eq "0" ]; then
      echo -e "\033[0;32mExtra tests passed\033[0m"
    else
      echo -e "\033[0;31mExtra tests failed\033[0m"
      (( ERROR += $retcode ))
    fi
  else
    echo "Did not find ${EXTRA_TESTS}"
  fi
else
  echo "Skipping extra-tests.sh, did not input an environment name as argument 1"
fi

# Do a pip dependencies check
echo "pip_check_start"
if [ -x "$(command -v pip)" ]; then
  pip check
  # Temporarily disable failure: too many false errors from bad metadata
  # (( ERROR += $? ))
fi
echo "pip_check_end"

# Do a security audit check
echo "pip_audit_start"
if [ -x "$(command -v pip-audit)" ]; then
  echo "pip audit results:"
  python pip_audit_markdown.py
  (( ERROR += $? ))
else
  echo "pip-audit not installed"
  (( ERROR += 1 ))
fi
echo "pip_audit_end"

exit $ERROR

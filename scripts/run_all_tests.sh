ERROR=0
ERR_PKGS=""
WARN_PKGS=""
RETRIES=5

for dir in *
do
  retries=$RETRIES
  if [ -f "${dir}/run_tests.py" ]; then
    echo "Running tests for ${dir}"
    pushd "${dir}"
    # Check on the repo for debugging purposes
    git status
    git rev-parse HEAD
    # Try a few times. Allow pass with a warning for race conditions in tests.
    while [ $retries -gt 0 ]; do
      timeout 5m python run_tests.py
      # Accumulate error codes, else the loop eats them
      retcode=$?
      if [ "${retcode}" -eq "0" ]; then
        break
      else
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
  fi
done

# If ERROR is nonzero, at least one of the run_test.py calls failed
if [ -n "${ERR_PKGS}" ]; then
  echo -e "\033[0;31mThe following packages failed all retries:${ERR_PKGS}\033[0m"
fi
if [ -n "${WARN_PKGS}" ]; then
  echo -e "\033[0;33mThe following packages had race conditions, but passed at least once:${WARN_PKGS}\033[0m"
fi

exit $ERROR

# Now that all the normal tests have passed, do the environment's extra tests if they exist
if [ -n "${1}" ]; then
  EXTRA_TESTS=envs/${1}/extra_tests.sh
  if [ -f "${EXTRA_TESTS}"]; then
    echo "Running ${EXTRA_TESTS}"
    bash "${EXTRA_TESTS}"
  else
    echo "Did not find ${EXTRA_TESTS}"
  fi
else
  echo "Did not input an environment name as argument 1"
fi

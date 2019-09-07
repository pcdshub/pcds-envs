ERROR=0
ERR_PKGS=""

for dir in *
do
  if [ -f "${dir}/run_tests.py" ]; then
    echo "Running tests for ${dir}"
    pushd "${dir}"
    # Check on the repo for debugging purposes
    git status
    git rev-parse HEAD
    python run_tests.py
    # Accumulate error codes, else the loop eats them
    retcode=$?
    if [ "${retcode}" -ne "0" ]; then
      ERR_PKGS="${ERR_PKGS}\n${dir}"
      color="31" # Red
    else
      color="32" # Green
    fi
    echo -e "\033[0;${color}mTest for ${dir} finished with exit code ${retcode}\033[0m"
    (( ERROR += $retcode ))
    popd
  fi
done

# If ERROR is nonzero, at least one of the run_test.py calls failed
if [ -n ${ERR_PKGS} ]; then
  echo -e "\033[0;31mThe following packages had errors:${ERR_PKGS}\033[0m"
fi

exit $ERROR

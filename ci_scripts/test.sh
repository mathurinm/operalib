set -e

# Get into a temp directory to run test from the installed scikit learn and
# check if we do not leave artifacts
mkdir -p $TEST_DIR

cd $TEST_DIR

if [[ "$COVERAGE" == "true" ]]; then
    py.test $MODULE --doctest-modules --cov-report=html --cov=$MODULE
else
    py.test $MODULE
fi

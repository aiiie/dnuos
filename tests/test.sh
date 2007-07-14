abspath() { ( cd "$1" ; pwd ; ) ; }

export DATA_DIR="`abspath ~/share/dnuos/testdata/`"
BASEDIR=`dirname $0`
BASEDIR=`abspath $BASEDIR/..`

unit_tests() {
    pushd $BASEDIR/dnuos > /dev/null
    nosetests --with-doctest -v
    RV=$?
    popd > /dev/null
    return $RV
}

func_doctests() {
    pushd $BASEDIR/tests > /dev/null
    nosetests --with-doctest -v "$BASEDIR/tests/functional"
    RV=$?
    popd > /dev/null
    return $RV
}

(
echo Unit tests
echo ==========
unit_tests &&

echo &&
echo Functional tests &&
echo ================ &&
func_doctests
)

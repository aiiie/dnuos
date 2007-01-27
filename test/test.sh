abspath() { ( cd "$1" ; pwd ; ) ; }

DATA_DIR="`abspath ~/share/dnuos/testdata/`"
REF_DIR="`abspath ~/share/dnuos/refoutput/`"
PYTHON='python'
BASEDIR=`dirname $0`
BASEDIR=`abspath $BASEDIR/../src`

func_test() {
    rm -f ~/.dnuos/dirs.pkl
    CMD="PYTHONPATH=$PYTHONPATH:$BASEDIR $PYTHON -c 'import dnuos.dnuos ; dnuos.dnuos.main()' $1"
    pushd $DATA_DIR > /dev/null
    (
    echo -n "test empty $2 ... " &&
    eval "$CMD" &&
    echo "ok" &&
    echo -n "test cache $2 ... " &&
    eval "$CMD" &&
    echo "ok"
    )
    RV=$?
    popd > /dev/null
    return $RV
}

func_test_piped() {
    REF="$REF_DIR/$1" ; shift
    func_test "$* -q | diff -U5 $REF -" "dnuos $*"
}

unit_tests() {
    pushd $BASEDIR > /dev/null
    nosetests --with-doctest -v
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
func_test_piped default aac lame &&
func_test_piped version -V &&
func_test_piped merge -m merge1/* merge2/* &&
func_test_piped outputdb --template db aac lame &&
func_test_piped strip -s aac &&
func_test_piped 'case' -i 'case' &&
func_test_piped broken broken &&
func_test "-O /tmp/output aac lame -q ; diff -U5 $REF_DIR/outputdb /tmp/output" 'dnuos -O /tmp/output aac lame'
)

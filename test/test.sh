abspath() { ( cd "$1" ; pwd ; ) ; }

DATA_DIR="`abspath ~/share/dnuos/testdata/`"
REF_DIR="`abspath ~/share/dnuos/refoutput/`"
PYTHON='python'
BASEDIR=`dirname $0`
BASEDIR=`abspath $BASEDIR/../src`

do_test() {
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
    popd > /dev/null
}

do_piped_test() {
    REF="$REF_DIR/$1" ; shift
    do_test "$* -q | diff -U5 $REF -" "dnuos $*"
}

(
echo Unit tests
echo ==========
nosetests --with-doctest -v &&

echo &&
echo Functional tests &&
echo ================ &&
do_piped_test default aac lame &&
do_piped_test version -V &&
do_piped_test merge -m merge1/* merge2/* &&
do_piped_test outputdb --template db aac lame &&
do_piped_test strip -s aac &&
do_piped_test 'case' -i 'case' &&
do_piped_test broken broken &&
do_test "-O /tmp/output aac lame -q ; diff -U5 $REF_DIR/outputdb /tmp/output" 'dnuos -O /tmp/output aac lame'
)

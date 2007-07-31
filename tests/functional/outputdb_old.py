"""
>>> test()
"""

from cStringIO import StringIO
import sys

from functest import process_args
from functest import get_unified_diff
import dnuos

def test():
    """Verify output-db with old deprecated option"""

    output = StringIO()
    old = sys.argv, sys.stderr, sys.stdout
    sys.argv = process_args("-q --output-db=/tmp/output aac lame")
    sys.argv.insert(0, 'dnuos')
    sys.stderr = sys.stdout = output
    dnuos.main()
    sys.argv, sys.stderr, sys.stdout = old

    expected_stdout_and_stderr = """
DeprecationWarning: The --output-db option is deprecated and will be removed in a future version. Use --template=db --file=FILE instead to ensure compatibility with future versions.
    """
    result = get_unified_diff(expected_stdout_and_stderr, output.getvalue())
    sys.stdout.write(result)

    expected_file = """
4:'jerk',4:'jerk',3:'AAC',0:'',1,96,131
    """
    output = open('/tmp/output').read()
    result = get_unified_diff(expected_file, output)
    sys.stdout.write(result)

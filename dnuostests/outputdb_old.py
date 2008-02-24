"""
>>> test()
"""

import os
import sys
from cStringIO import StringIO
from tempfile import mktemp

import dnuos

from dnuostests.functest import process_args
from dnuostests.functest import get_unified_diff

def test():
    """Verify output-db with old deprecated option"""

    output = StringIO()
    old = sys.argv, sys.stderr, sys.stdout
    output_path = mktemp()
    try:
        sys.argv = process_args("-q --output-db=%s aac lame" % output_path)
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

        output_file = open(output_path, 'rb')
        try:
            result = get_unified_diff(expected_file, output_file.read())
            sys.stdout.write(result)
        finally:
            output_file.close()
    finally:
        os.remove(output_path)

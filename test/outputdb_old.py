"""
>>> test()
"""

from cStringIO import StringIO
from functest import process_args, write_unified_diff
import dnuos

def test():
    args = process_args("-q --output-db=/tmp/output aac lame")
    output = StringIO()
    dnuos.main(args, output, output)

    expected_stdout_and_stderr = """
DeprecationWarning: The --output-db option is deprecated and will be removed in a future version. Use --template=db --file=FILE instead to ensure compatibility with future versions.
    """
    write_unified_diff(expected_stdout_and_stderr, output.getvalue())

    expected_file = """
9:'('jerk',)',9:'('jerk',)',3:'AAC',0:'',1,320,225807135759696384
    """
    output = open('/tmp/output').read()
    write_unified_diff(expected_file, output)

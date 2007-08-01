"""
>>> test()
"""

import os.path
import sys

from dnuostests.functest import write_dnuos_diff

def test():
    """Verify no-args-behavoiur"""

    write_dnuos_diff("", """
No folders to process.
Type `dnuos -h' for help.
""")

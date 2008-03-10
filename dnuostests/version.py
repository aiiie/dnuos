"""
>>> test()
"""

import dnuos
from dnuostests.functest import write_dnuos_diff

def test():
    """Verify version string output"""

    write_dnuos_diff("-V", """
dnuos %s
""" % dnuos.__version__)

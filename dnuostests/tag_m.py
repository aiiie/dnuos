"""
>>> test()
"""

import os
import time

from dnuostests.functest import write_dnuos_diff

def test():
    """Verify output tag m"""

    old_tz = os.environ.get('TZ', '')
    os.environ['TZ'] = 'GMT'
    time.tzset()
    write_dnuos_diff('-q --output=[m] aac', """
Modified
========

Sat Jul 14 17:39:39 2007
Sat Jul 14 18:39:40 2007
    """)
    os.environ['TZ'] = old_tz

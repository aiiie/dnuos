"""
>>> test()
"""

import os
import time

from dnuostests.functest import write_dnuos_diff

def test():
    """Verify output tag M"""

    curtime = int(time.time())
    for path in (('test1', 'faac.m4a'),
                 ('test2', '_ 15 - Tom Cat Blues.m4a')):
        os.utime(os.path.join(os.environ['DATA_DIR'], 'aac', *path),
                 (curtime, curtime))
    write_dnuos_diff('-q --output=[M] aac', """
Modified
========

%s
%s
    """ % (curtime, curtime))

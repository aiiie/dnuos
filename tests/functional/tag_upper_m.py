"""
>>> test()
"""

from functest import write_dnuos_diff

def test():
    """Verify output tag M"""

    write_dnuos_diff('-q --output=[M] aac', """
Modified
========

1184434779
1184438380
    """)

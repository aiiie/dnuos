"""
>>> test()
"""

from functest import write_dnuos_diff

def test():
    write_dnuos_diff("", """
No folders to process.
Type 'dnuos.py -h' for help.
    """)

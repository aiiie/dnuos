"""
>>> test()
"""

from functest import write_dnuos_diff

def test():
    write_dnuos_diff("-q --template=db aac lame", """
9:'('jerk',)',9:'('jerk',)',3:'AAC',0:'',1,320,225807135759696384
    """)

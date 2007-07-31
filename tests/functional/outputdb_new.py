"""
>>> test()
"""

from functest import write_dnuos_diff

def test():
    """Verify output-db with new --template option"""

    write_dnuos_diff("-q --template=db aac lame", """
4:'jerk',4:'jerk',3:'AAC',0:'',1,96,131
    """)

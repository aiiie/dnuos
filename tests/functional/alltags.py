"""
>>> test()
"""

from functest import write_dnuos_diff

def test():
    write_dnuos_diff('--output="[a]|[A]|[b]|[B]|[C]" aac', """
    """)
    write_dnuos_diff('--output="[D]|[f]|[l]|[L]|[M]" aac', """
    """)
    write_dnuos_diff('--output="[m]|[n]|[N]|[p]|[P]" aac', """
    """)
    write_dnuos_diff('--output="[q]|[s]|[S]|[t]|[T]" aac', """
    """)

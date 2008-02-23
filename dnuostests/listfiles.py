"""
>>> test()
"""

from dnuostests.functest import write_dnuos_diff

def test():
    """Verify individual file listing functionality"""

    write_dnuos_diff("-qs -L --output=[n],[a],[A],[b],[C],[f],[l],[L],[p],"
                     "[q],[s],[t],[T],[V] nonlame",
"""
    lame,VBR,,15.7k,,1,0:12,12,-V9n,-V9n,23.3k,MP3,V,LAME3.97b
        397b1-v9-vbrnew.mp3,VBR,,15.7k,,1,0:12,12,-V9n,-V9n,23.3k,MP3,V,LAME3.97b
    twolame,8,,8.00k,,1,0:24,24,,8 C,23.6k,MP3,C,
        twolame.mp3,8,,8.00k,,1,0:24,24,,8 C,23.6k,MP3,C,
""")

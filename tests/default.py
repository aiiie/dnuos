"""
>>> test()
"""

from functest import write_dnuos_diff

def test():
    write_dnuos_diff("-q aac lame", """
Album/Artist                                        |  Size | Type | Quality
============================================================================
aac                                                 |       |      | 
    test1                                           | 1.55M | AAC  | 320 C
    test2                                           | 1.55M | AAC  | 320 C
lame                                                |       |      | 
    3903-ape                                        |  131k | MP3  | -ape
    3903-apfe                                       |  146k | MP3  | -apfe
    3903-apfs                                       |  125k | MP3  | -apfs
    3903-api                                        |  237k | MP3  | -api
    3903-aps                                        |  101k | MP3  | -aps
    3961-ape                                        |  116k | MP3  | -V 0
    3961-apfe                                       |  117k | MP3  | -V 0 --vbr-new
    3961-apfm                                       | 81.3k | MP3  | -V 4 --vbr-new
    3961-apfs                                       |  100k | MP3  | -V 2 --vbr-new
    3961-api                                        |  237k | MP3  | -b 320
    3961-apm                                        | 73.0k | MP3  | -V 4
    3961-aps                                        |  102k | MP3  | -V 2
    397b1-b320                                      |  237k | MP3  | -b 320
    397b1-v0                                        |  106k | MP3  | -V 0
    397b1-v0-vbrnew                                 |  107k | MP3  | -V 0 --vbr-new
    397b1-v1                                        | 98.1k | MP3  | -V 1
    397b1-v1-vbrnew                                 | 95.5k | MP3  | -V 1 --vbr-new
    397b1-v2                                        | 88.6k | MP3  | -V 2
    397b1-v2-vbrnew                                 | 83.6k | MP3  | -V 2 --vbr-new
    397b1-v3                                        | 84.4k | MP3  | -V 3
    397b1-v3-vbrnew                                 | 79.0k | MP3  | -V 3 --vbr-new
    397b1-v4                                        | 77.3k | MP3  | -V 4
    397b1-v4-vbrnew                                 | 73.4k | MP3  | -V 4 --vbr-new
    397b1-v5                                        | 63.3k | MP3  | -V 5
    397b1-v5-vbrnew                                 | 60.5k | MP3  | -V 5 --vbr-new
    397b1-v6                                        | 54.6k | MP3  | -V 6
    397b1-v6-vbrnew                                 | 51.9k | MP3  | -V 6 --vbr-new
    397b1-v7                                        | 44.4k | MP3  | -V 7
    397b1-v7-vbrnew                                 | 41.1k | MP3  | -V 7 --vbr-new
    397b1-v8                                        | 37.7k | MP3  | -V 8
    397b1-v8-vbrnew                                 | 34.1k | MP3  | -V 8 --vbr-new
    397b1-v9                                        | 26.9k | MP3  | -V 9
    397b1-v9-vbrnew                                 | 23.3k | MP3  | -V 9 --vbr-new
    """)
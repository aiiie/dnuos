"""
>>> test()
"""

import os
import sys
from cStringIO import StringIO

import dnuos
import dnuos.appdata
import dnuos.audiodir
import dnuos.path

def test():
    """Verify caching functionality"""

    old = sys.argv, sys.stderr, sys.stdout
    old_cwd = os.getcwd()
    cache_file = dnuos.appdata.user_data_file('dirs', '.')
    os.chdir(os.environ['DATA_DIR'])
    try:
        output = StringIO()
        sys.argv = ['dnuos', '-q', '--cache-dir=.', '.']
        sys.stderr = sys.stdout = output
        try:
            dnuos.main(locale='C')
        finally:
            sys.argv, sys.stderr, sys.stdout = old
        cache = dnuos.setup_cache(cache_file)
        assert cache.version == dnuos.audiodir.Dir.__version__
        for path, adir in cache.iteritems():
            assert dnuos.path.isdir(path)
            adir2 = dnuos.audiodir.Dir(path)
            assert adir.albums == adir2.albums
            assert adir.artists == adir2.artists
            assert adir._audio_files == adir2._audio_files
            assert adir._bad_files == adir2._bad_files
            assert adir._bitrates == adir2._bitrates
            assert adir._lengths == adir2._lengths
            assert adir._types == adir2._types
            assert adir.modified == adir2.modified
            assert adir.path == adir2.path
            assert adir._profiles == adir2._profiles
            assert adir.sizes == adir2.sizes
            assert adir._vendors == adir2._vendors
    finally:
        try:
            os.remove(cache_file)
        except OSError:
            pass
        os.chdir(old_cwd)

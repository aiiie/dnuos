"""Module dealing with application data.

Most of this comes from
http://mail.python.org/pipermail/python-list/2005-September/341702.html
"""

import os
import sys


def user_data_dir(appname, vendor, version=None):
    """Return full path to the user-specific data dir for this application.

        "appname" is the name of application.
        "vendor" (only required and used on Windows) is the name of the
            owner or distributing body for this application. Typically
            it is the owning company name.
        "version" is an optional version path element to append to the
            path. You might want to use this if you want multiple versions
            of your app to be able to run independently. If used, this
            would typically be "<major>.<minor>".

    Typical user data directories are:
        Windows:    C:\Documents and Settings\USER\Application Data\<owner>\<appname>
        Mac OS X:   ~/Library/Application Support/<appname>
        Unix:       ~/.<lowercased-appname>

    >>> import os
    >>> dir_ = user_data_dir('Dnuos', 'Dnuos')
    >>> if dir_.endswith(os.path.sep):
    ...     dir_ = os.path.dirname(dir_)
    ...
    >>> dir_ = os.path.dirname(dir_)
    >>> if sys.platform.startswith('win'):
    ...     os.path.isdir(os.path.dirname(dir_))
    ... else:
    ...     os.path.isdir(dir_)
    ...
    True
    """

    path = None
    if sys.platform.startswith('win'):
        # Try to make this a unicode path because SHGetFolderPath does
        # not return unicode strings when there is unicode data in the
        # path.
        try:
            from win32com.shell import shellcon, shell
            path = shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0)
        except ImportError:
            path = os.environ['APPDATA']
        try:
            path = unicode(path)
        except UnicodeError:
            pass
        path = os.path.join(path, vendor, appname)
    elif sys.platform == 'darwin':
        try:
            from Carbon import Folder, Folders
            path = Folder.FSFindFolder(Folders.kUserDomain,
                                       Folders.kApplicationSupportFolderType,
                                       Folders.kDontCreateFolder)
            path = os.path.join(path.FSRefMakePath(), appname)
        except (ImportError, AttributeError):
            pass
    if not path:
        path = os.path.expanduser('~/.' + appname.lower())

    if version:
        path = os.path.join(path, version)
    return path


def create_user_data_dir(dir_):
    """Creates user data directory"""

    if not os.path.exists(dir_):
        os.makedirs(dir_)


def user_data_file(filename, dir_):
    """Gets full path to user data file"""

    return os.path.join(dir_, filename)

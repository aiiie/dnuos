import os
import sys

"""
Most of this comes from
http://mail.python.org/pipermail/python-list/2005-September/341702.html
"""

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
    """
    if sys.platform.startswith('win'):
        # Try to make this a unicode path because SHGetFolderPath does
        # not return unicode strings when there is unicode data in the
        # path.
        try:
            from win32com.shell import shellcon, shell
            path = shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0)
        except ImportError:
            path = os.environ('APPDATA')
        try:
            path = unicode(path)
        except UnicodeError:
            pass
        path = os.path.join(path, vendor, appname)
    elif sys.platform == 'darwin':
        from Carbon import Folder, Folders
        path = Folder.FSFindFolder(Folders.kUserDomain,
                                   Folders.kApplicationSupportFolderType,
                                   Folders.kDontCreateFolder)
        path = os.path.join(path.FSRefMakePath(), appname)
    else:
        path = os.path.expanduser('~/.' + appname.lower())

    if version:
        path = os.path.join(path, version)
    return path

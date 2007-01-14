import errno
import os

import appdata


USER_DATA_DIR = appdata.user_data_dir('Dnuos', 'Dnuos')


def create_user_data_dir():
    try:
        os.mkdir(USER_DATA_DIR)
    except OSError, e:
        if e.errno != errno.EEXIST:
            raise e


def user_data_file(filename):
    return os.path.join(USER_DATA_DIR, filename)

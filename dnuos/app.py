import errno
import os

import appdata


USER_DATA_DIR = appdata.user_data_dir('Dnuos', 'Dnuos')


def create_user_data_dir():
    if not os.path.exists(USER_DATA_DIR):
        os.makedirs(USER_DATA_DIR)


def user_data_file(filename):
    return os.path.join(USER_DATA_DIR, filename)

import appdata


USER_DATA_DIR = appdata.user_data_dir('Dnuos', 'Dnuos')


def create_user_data_dir():
    os.path.mkdir(USER_DATA_DIR)


def user_data_file(filename):
    return os.path.join(USER_DATA_DIR, filename)

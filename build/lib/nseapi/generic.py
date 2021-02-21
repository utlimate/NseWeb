import os


def validate_directory(dir_path: str):
    """ This will create new directory if not exist """

    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    return True
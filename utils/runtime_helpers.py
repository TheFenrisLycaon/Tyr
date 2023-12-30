import os
from constants import const

def get_relative_path():
    if const.DEV_ENV:
        # from google.appengine.tools.devappserver2.python import sandbox
        # sandbox._WHITE_LIST_C_MODULES += ['_ctypes', 'gestalt']
        temp_dir = os.path.join(const.ROOT_DIRECTORY, "src")
    else:
        temp_dir = os.path.join(const.ROOT_DIRECTORY, "dist")

    curr_path = os.path.abspath(os.path.dirname(__file__))

    return temp_dir
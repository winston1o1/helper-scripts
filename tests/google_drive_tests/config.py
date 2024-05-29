from os import path
import sys

class Config:
    MAIN_MODULE_PATH = path.dirname(path.dirname(path.dirname(__file__)))
    SRC_FILES_MODULE_PATH = path.join(MAIN_MODULE_PATH,"helper_scripts")
    GOOGLE_DRIVE_SECRETS_JSON_PATH = path.join(path.dirname(__file__),"service_account_dev.json")

def add_module_path_to_sys_path():
    sys.path.append(Config.MAIN_MODULE_PATH)
    sys.path.append(Config.SRC_FILES_MODULE_PATH)


add_module_path_to_sys_path()


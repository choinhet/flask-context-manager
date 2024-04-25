from flask_context_manager.src.main.util.key_utility import KeyUtility


@KeyUtility.auto_set_key
class BaseKey:
    FOLDERS: str
    IGNORE: str

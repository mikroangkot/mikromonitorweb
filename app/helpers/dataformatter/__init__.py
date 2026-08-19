from .custom_ui import FormatUI
from .custom_log import DataLog
from .custom_pass import PasswordBcrypt
from .custom_sharedpreferences import AppStorage
from .custom_decode import DecodeToken


class DataFormatter(FormatUI, DataLog, PasswordBcrypt, AppStorage, DecodeToken):
    pass

from .custom_ui import FormatUI
from .custom_log import DataLog
from .custom_pass import PasswordBcrypt
from .custom_sharedpreferences import AppStorage
from .custom_decode import DecodeToken
from .custom_datetime import FormatDatetime
from .custom_dispatcher import FormatDispatcher


class DataFormatter(
    FormatUI,
    DataLog,
    PasswordBcrypt,
    AppStorage,
    DecodeToken,
    FormatDatetime,
    FormatDispatcher
):
    pass

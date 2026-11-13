from .signin import SigninApp
from .infoapp import InfoApp
from .signup import SignupApp
from .useractivity import UserActivity
from .dataunit import DataUnit
from .datakmbaku import DataKmBaku
from .usersactivityreport import UsersActivityReport


class Api(SigninApp, InfoApp, SignupApp, UserActivity, DataUnit, DataKmBaku, UsersActivityReport):
    pass
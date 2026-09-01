from .signin import SigninApp
from .infoapp import InfoApp
from .signup import SignupApp
from .useractivity import UserActivity
from .useractivity_sync import UserActivitySync
from .dataunit import DataUnit
from .datakmbaku import DataKmBaku


class Api(SigninApp, InfoApp, SignupApp, UserActivity, UserActivitySync, DataUnit, DataKmBaku):
    pass
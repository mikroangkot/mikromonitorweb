from .signin import SigninApp
from .infoapp import InfoApp
from .signup import SignupApp
from .useractivity import UserActivity
from .useractivity_sync import UserActivitySync
from .dataunit import DataUnit


class Api(SigninApp, InfoApp, SignupApp, UserActivity, UserActivitySync, DataUnit):
    pass
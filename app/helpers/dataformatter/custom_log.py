from datetime import datetime


class DataLog:

    @staticmethod
    def log_msg(message, tag="INFO"):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        yellow = "\033[1;33m"
        reset = "\033[0m"
        print(f"{current_time} {yellow}[{tag.upper()}]{reset}: {str(message).lower()}")
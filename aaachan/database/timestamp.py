from datetime import datetime
from time import time

class Timestamp():
    @staticmethod
    def now() -> str:
        return datetime.fromtimestamp(time()).strftime('%Y-%m-%d %H:%M:%S')


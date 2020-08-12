from datetime import datetime
from time import time

class Timestamp():
    @staticmethod
    def now_dt() -> datetime:
        return datetime.fromtimestamp(time())

    @staticmethod
    def now() -> str:
        return Timestamp().now_dt().strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def passed(before: str, seconds: int) -> bool:
        return before.strip() == '' or seconds <= (
                Timestamp().now_dt() -
                datetime.strptime(before, '%Y-%m-%d %H:%M:%S')
                ).total_seconds()

    @staticmethod
    def diff_str(before: str, seconds: int) -> str:
        delta_ts = seconds - (Timestamp().now_dt() -
                datetime.strptime(before, '%Y-%m-%d %H:%M:%S')
                ).total_seconds()

        mins = int((delta_ts % 3600) // 60)
        secs = int(delta_ts % 60)

        return '{:02d}:{:02d}'.format(mins, secs)


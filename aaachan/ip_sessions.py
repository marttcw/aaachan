from .timestamp import Timestamp

class IpSessions():
    def __init__(self,
            seconds_limit_thread: int = (5 * 60),
            seconds_limit_post: int = 60):
        self.__ips = {}
        self.__secs_thr_lim = seconds_limit_thread
        self.__secs_post_lim = seconds_limit_post

    def __setup(self, ip_addr: str):
        if ip_addr not in self.__ips:
            self.__ips[ip_addr] = {
                    'thread_limit': '',
                    'post_limit': ''
            }

    def start_thread_limit(self, ip_addr: str):
        self.__setup(ip_addr)
        self.__ips[ip_addr]['thread_limit'] = Timestamp.now()

    def start_post_limit(self, ip_addr: str):
        self.__setup(ip_addr)
        self.__ips[ip_addr]['post_limit'] = Timestamp.now()

    def allow_thread(self, ip_addr: str) -> bool:
        self.__setup(ip_addr)
        return Timestamp.passed(self.__ips[ip_addr]['thread_limit'], self.__secs_thr_lim)

    def allow_post(self, ip_addr: str) -> bool:
        self.__setup(ip_addr)
        return Timestamp.passed(self.__ips[ip_addr]['post_limit'], self.__secs_post_lim)


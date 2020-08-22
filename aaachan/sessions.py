import os

SESSION_ID_SIZE = 64

class Sessions():
    def __init__(self):
        self.__sessions = {}

    def add(self, username: str, utype: str) -> str:
        sid = str(os.urandom(SESSION_ID_SIZE))

        self.__sessions[sid] = {
                'username': username,
                'type': utype
        }

        return sid

    def exists(self, sid: str) -> bool:
        return sid in self.__sessions

    def type(self, sid: str) -> str:
        if sid in self.__sessions:
            return self.__sessions[sid]['type']
        else:
            return None

    def remove(self, sid: str):
        self.__sessions.pop(sid, None)


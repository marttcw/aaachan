import os

SESSION_ID_SIZE = 64

class Sessions():
    def __init__(self):
        self.__sessions = {}

    def add(self, username: str) -> str:
        sid = str(os.urandom(SESSION_ID_SIZE))

        self.__sessions[sid] = {
                'username': username
        }

        return sid

    def exists(self, sid: str) -> bool:
        return sid in self.__sessions

    def remove(self, sid: str):
        self.__sessions.pop(sid, None)


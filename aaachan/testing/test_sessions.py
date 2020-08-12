import pytest
from aaachan.sessions import Sessions

def test_user_add():
    sessions = Sessions()
    sid = sessions.add('john')
    assert sessions.exists(sid) == True
    sessions.remove(sid)
    assert sessions.exists(sid) == False

def test_nonexist_sid():
    sessions = Sessions()
    assert sessions.exists('aaaaaa') == False


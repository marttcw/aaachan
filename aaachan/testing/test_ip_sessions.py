import pytest
from aaachan.ip_sessions import IpSessions

def test_thread_limit_posted():
    ip_sessions = IpSessions()
    ip_sessions.start_thread_limit('192.168.1.1')
    assert ip_sessions.allow_thread('192.168.1.1') == False

def test_thread_limit_not_posted():
    ip_sessions = IpSessions()
    assert ip_sessions.allow_thread('192.168.1.1') == True


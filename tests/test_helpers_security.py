import pytest

import helpers.security as helpers_security


class DummyHeaders(dict):
    """Mimics Tornado HTTPHeaders.get behaviour."""

    def get(self, key, default=None):
        return super().get(key, default)


class DummyRequest:
    def __init__(self, headers=None, remote_ip=None, host=None):
        self.headers = DummyHeaders(headers or {})
        self.remote_ip = remote_ip
        self.host = host


def test_is_request_from_localhost_with_loopback_ip(monkeypatch):
    request = DummyRequest(headers={"X-Forwarded-For": "127.0.0.1"})
    monkeypatch.setattr(helpers_security, "_get_current_request", lambda: request)
    monkeypatch.setattr(helpers_security, "_get_server_address", lambda: "localhost")

    assert helpers_security.is_request_from_localhost() is True


def test_is_request_from_localhost_with_localhost_host_header(monkeypatch):
    request = DummyRequest(headers={"Host": "localhost:8501"}, remote_ip="198.51.100.10")
    monkeypatch.setattr(helpers_security, "_get_current_request", lambda: request)
    monkeypatch.setattr(helpers_security, "_get_server_address", lambda: "localhost")

    assert helpers_security.is_request_from_localhost() is True


@pytest.mark.parametrize(
    "headers, remote_ip",
    [
        ({}, "203.0.113.10"),
        ({"X-Forwarded-For": "203.0.113.10"}, None),
        ({"Host": "mc-test.example.com"}, "203.0.113.10"),
    ],
)
def test_is_request_from_localhost_denies_remote_access(monkeypatch, headers, remote_ip):
    request = DummyRequest(headers=headers, remote_ip=remote_ip)
    monkeypatch.setattr(helpers_security, "_get_current_request", lambda: request)
    monkeypatch.setattr(helpers_security, "_get_server_address", lambda: "0.0.0.0")

    assert helpers_security.is_request_from_localhost() is False

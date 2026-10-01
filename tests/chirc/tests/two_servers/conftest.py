import pytest
from chirc.tests.common.sessions import IRCNetworkSession


@pytest.fixture
def irc_network_session(request):
    chirc_exe = request.config.getoption("--chirc-exe")
    chirc_loglevel = request.config.getoption("--chirc-loglevel")
    chirc_port = request.config.getoption("--chirc-port")

    session = IRCNetworkSession(chirc_exe=chirc_exe,
                                loglevel=chirc_loglevel,
                                default_start_port=chirc_port)

    yield session

    session.end_sessions()


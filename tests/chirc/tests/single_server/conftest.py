import pytest
from chirc.tests.common.sessions import SingleIRCSession


@pytest.fixture
def irc_session(request):   
    chirc_exe = request.config.getoption("--chirc-exe")
    chirc_loglevel = request.config.getoption("--chirc-loglevel")
    chirc_port = request.config.getoption("--chirc-port")
    external_chirc_port = request.config.getoption("--chirc-external-port")
    
    session = SingleIRCSession(chirc_exe=chirc_exe,
                               loglevel=chirc_loglevel,
                               chirc_port=chirc_port,
                               external_chirc_port=external_chirc_port)
    
    session.start_session()
    
    def fin():
        session.end_session()
        
    request.addfinalizer(fin)    
    
    return session

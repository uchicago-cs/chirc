import pytest
import os.path
from chirc.tests.common import IRCSession
    
def pytest_addoption(parser):
    parser.addoption("-C", action="store", metavar="CATEGORY_ID",
        help="only run tests in category CATEGORY_ID.")    
    parser.addoption("--chirc-exe", action="store", metavar="CHIRC_EXE",
        help="set location of chirc executable")       
    parser.addoption("--chirc-loglevel", action="store", type=int, metavar="LOGLEVEL",
        help="set log level in chirc to LOGLEVEL (-1: -q, 0: normal, 1: -v, 2: --v).")       
    parser.addoption("--chirc-port", action="store", type=int,
        help="port to run server on")       
    parser.addoption("--randomize-ports", action="store_true",
        help="randomize server's port when running tests")       

@pytest.fixture
def irc_session(request):   
    chirc_exe = request.config.getoption("--chirc-exe")
    chirc_loglevel = request.config.getoption("--chirc-loglevel")
    chirc_port = request.config.getoption("--chirc-port")
    randomize_ports = request.config.getoption("--randomize-ports")
    
    session = IRCSession(chirc_exe = chirc_exe, 
                         loglevel = chirc_loglevel, 
                         default_port = chirc_port,
                         randomize_ports=randomize_ports)
    
    session.start_session()
    
    def fin():
        session.end_session()
        
    request.addfinalizer(fin)    
    
    return session

def pytest_configure(config):
    f = open("alltests", "w")
    f.close()

def pytest_itemcollected(item):
    category_marker = item.get_marker("category")
    if category_marker is not None:
        category = category_marker.args[0]
        with open("alltests", "a") as f:
            f.write("{},{}\n".format(category, item.nodeid))

def pytest_runtest_setup(item):
    only_category = item.config.getoption("-C")
    if only_category is not None:    
        category_marker = item.get_marker("category")
        if category_marker is not None:
            category = category_marker.args[0]
            if category != item.config.getoption("-C"):
                pytest.skip("Only running tests in category {}".format(only_category))

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    outcome = yield
    report = outcome.get_result()
    category = item.get_marker("category").args[0]

    if report.when == "call":
        report.metadata = {
            'category': category
        }        
        report.test_metadata = {
            'category': category
        }
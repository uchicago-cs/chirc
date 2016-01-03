import pytest
from chirc.types import ReplyTimeoutException

@pytest.mark.category("PING_PONG")
class TestPING(object):

    def test_ping(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("PING")

        reply = irc_session.get_message(client1, expect_cmd = "PONG", expect_nparams = 1)        
        
    def _test_multiping(self, irc_session, numclients, will_ping):
        clients = []
        for i in range(numclients):
            nick = "user%i" % (i+1)
            username = "User %s" % nick
            client =  irc_session.connect_user(nick, username)
            clients.append( (nick, client) )
            
        for i in range(will_ping):
            clients[i][1].send_cmd("PING")
            
        for i in range(will_ping):
            irc_session.get_message(clients[i][1], expect_cmd = "PONG", expect_nparams = 1)
        
    def test_multiping1(self, irc_session):
        self._test_multiping(irc_session, 5, 5)
        
    def test_multiping2(self, irc_session):
        self._test_multiping(irc_session, 10, 5)        
        
    def test_multiping3(self, irc_session):
        self._test_multiping(irc_session, 20, 15)        

    def test_multiping4(self, irc_session):
        self._test_multiping(irc_session, 50, 35)        

@pytest.mark.category("PING_PONG")
class TestPONG(object):

    def test_pong(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("PONG")

        with pytest.raises(ReplyTimeoutException):
            irc_session.get_reply(client1)    

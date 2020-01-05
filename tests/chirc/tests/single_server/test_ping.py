import pytest

@pytest.mark.category("PING_PONG")
class TestPING(object):

    def test_ping(self, irc_session):
        """
        Test sending a PING to the server, which should reply with a PONG.
        """
        
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("PING")

        irc_session.get_message(client1, expect_cmd = "PONG", expect_nparams = 1)        
        
    #
    # The following tests are not so much a test of the PING command,
    # but a basic test of whether replies will leak from one client to another
    # (i.e., make sure there aren't any bugs that make the server send
    # messages to clients that shouldn't be getting them)
    #
        
    def _test_multiping(self, irc_session, numclients, will_ping):
        """
        Connects `numclients` clients to the server, and has the first
        `will_ping` clients PING the server. Only they should receive
        a PONG back.
        """
        
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
        """
        Test five users connecting to the server and pinging it.
        """        
        self._test_multiping(irc_session, 5, 5)
        
    def test_multiping2(self, irc_session):
        """
        Test ten users connecting to the server and five of them pinging it.
        """        
        self._test_multiping(irc_session, 10, 5)        
        
    def test_multiping3(self, irc_session):
        """
        Test twenty users connecting to the server and fifteen of them pinging it.
        """        
        self._test_multiping(irc_session, 20, 15)        

    def test_multiping4(self, irc_session):
        """
        Test fifty users connecting to the server and thirty-five of them pinging it.
        """        
        self._test_multiping(irc_session, 50, 35)        

@pytest.mark.category("PING_PONG")
class TestPONG(object):

    def test_pong(self, irc_session):
        """
        Test sending a PONG, which should receive no reply
        """
        
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("PONG")

        irc_session.get_reply(client1, expect_timeout = True)

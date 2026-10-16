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

    def _test_ping_token(self, irc_session, ping_param, token):
        """
        Sends a PING with a parameter, and checks that the PONG includes
        the same token as its last parameter (IRC clients rely on this
        to match PONGs to PINGs, e.g., to measure lag)
        """

        client1 = irc_session.connect_user("user1", "User One")

        client1.send_cmd("PING " + ping_param)

        msg = irc_session.get_message(client1, expect_cmd = "PONG", expect_nparams = 2)

        # The token may be sent back as a long parameter (with a colon) or not
        pong_token = msg.params[-1]
        if pong_token.startswith(":"):
            pong_token = pong_token[1:]

        assert pong_token == token, \
            "Expected the PONG to include the PING's token ({}), got {} instead\nMessage: {}".format(token, pong_token, msg.raw(bookends=True))

    def test_ping_token1(self, irc_session):
        """
        Test sending a PING with a token. The PONG should include the same token.
        """
        self._test_ping_token(irc_session, "abc123", "abc123")

    def test_ping_token2(self, irc_session):
        """
        Test sending a PING with a token in a long parameter, like some IRC
        clients do when measuring lag. The PONG should include the same token.
        """
        self._test_ping_token(irc_session, ":LAG1759671234", "LAG1759671234")

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

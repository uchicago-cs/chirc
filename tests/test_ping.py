import tests.replies as replies
import time
from tests.common import ChircTestCase, ChircClient, ReplyTimeoutException
from tests.scores import score

class PING(ChircTestCase):

    @score(category="PING_PONG")
    def test_ping(self):
        client1 = self._connect_user("user1", "User One")
        
        client1.send_cmd("PING")

        reply = self.get_message(client1, expect_cmd = "PONG", expect_nparams = 1)        
        
    @score(category="PING_PONG")
    def _test_multiping(self, numclients, will_ping):
        clients = []
        for i in range(numclients):
            nick = "user%i" % (i+1)
            username = "User %s" % nick
            client =  self._connect_user(nick, username)
            clients.append( (nick, client) )
            
        for i in range(will_ping):
            clients[i][1].send_cmd("PING")
            
        for i in range(will_ping):
            reply = self.get_message(clients[i][1], expect_cmd = "PONG", expect_nparams = 1)
        
    @score(category="PING_PONG")
    def test_multiping1(self):
        self._test_multiping(5, 5)
        
    @score(category="PING_PONG")
    def test_multiping2(self):
        self._test_multiping(10, 5)        
        
    @score(category="PING_PONG")
    def test_multiping3(self):
        self._test_multiping(20, 15)        

    @score(category="PING_PONG")
    def test_multiping4(self):
        self._test_multiping(50, 35)        

class PONG(ChircTestCase):

    @score(category="PING_PONG")
    def test_pong(self):
        client1 = self._connect_user("user1", "User One")
        
        client1.send_cmd("PONG")

        self.assertRaises(ReplyTimeoutException, self.get_reply, client1)    
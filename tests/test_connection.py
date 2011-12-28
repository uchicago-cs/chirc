import tests.replies as replies
import time
from tests.common import ChircTestCase, ChircClient
from tests.scores import score

class BasicConnection(ChircTestCase):

    @score(category="BASIC_CONNECTION")
    def test_connect_basic1(self):
        client = self.get_client()
        
        client.send_cmd("NICK user1")
        client.send_cmd("USER user1 * * :User One")
        
        self.get_reply(client, expect_code = replies.RPL_WELCOME, expect_nick="user1", expect_nparams = 1)

    @score(category="BASIC_CONNECTION")
    def test_connect_basic2(self):
        client = self.get_client()
        
        client.send_raw("NI")
        client.send_raw("CK ")
        client.send_raw("user1\r")
        client.send_raw("\n")
        client.send_raw("USER user")
        client.send_raw("1 * * ")
        client.send_raw(":Us")
        client.send_raw("er ")
        client.send_raw("One")
        client.send_raw("\r")
        client.send_raw("\n")
        
        self.get_reply(client, expect_code = replies.RPL_WELCOME, expect_nick="user1", expect_nparams = 1)

    @score(category="BASIC_CONNECTION")
    def test_connect_basic3(self):
        client = self.get_client()
        
        client.send_raw("NICK user1\r\nUSER user1 * * :User One\r\n")
        
        self.get_reply(client, expect_code = replies.RPL_WELCOME, expect_nick="user1", expect_nparams = 1)

class FullConnection(ChircTestCase):

    @score(category="CONNECTION_REGISTRATION")
    def test_connect_full1(self):
        client = self.get_client()
        
        client.send_cmd("NICK user1")
        client.send_cmd("USER user1 * * :User One")
        
        self._test_welcome_messages(client, "user1")   
        
    @score(category="CONNECTION_REGISTRATION")
    def test_connect_full2(self):
        client = self.get_client()
        
        client.send_cmd("USER user1 * * :User One")
        client.send_cmd("NICK user1")
        
        self._test_welcome_messages(client, "user1")           

    @score(category="CONNECTION_REGISTRATION")
    def test_connect_full3(self):
        client = self.get_client()
        
        client.send_cmd("NICK user1")
        client.send_cmd("USER user1 * * :User One")
        
        self._test_welcome_messages(client, "user1")
        self._test_lusers(client, "user1")
        self._test_motd(client, "user1")         
        
        
class MultiuserConnection(ChircTestCase):        
        
    @score(category="CONNECTION_REGISTRATION")
    def test_connect_2users(self):      
        self._connect_user("user1", "User One")
        self._connect_user("user2", "User Two")

    @score(category="CONNECTION_REGISTRATION")
    def test_connect_duplicate_nick(self):
        client1 = self._connect_user("user1", "User One")

        client2 = self.get_client()
        client2.send_cmd("NICK user1")
        reply = self.get_reply(client2, expect_code = replies.ERR_NICKNAMEINUSE, expect_nick = "*", expect_nparams = 2,
                               expect_short_params = ["user1"],
                               long_param_re = "Nickname is already in use")
        

import tests.replies as replies
import time
from tests.common import ChircTestCase, ChircClient, ReplyTimeoutException
from tests.scores import score

class Robustness(ChircTestCase):

    @score(category="ROBUST")
    def test_whitespace1(self):
        client = self.get_client()
        
        client.send_cmd("  ")
        
        self.assertRaises(ReplyTimeoutException, self.get_reply, client)                

    @score(category="ROBUST")
    def test_whitespace2(self):
        client = self.get_client()
        
        client.send_cmd(" NICK user1 ")
        client.send_cmd(" USER user1 * * :User One ")
        
        self.get_reply(client, expect_code = replies.RPL_WELCOME, expect_nick="user1", expect_nparams = 1)

    @score(category="ROBUST")
    def test_whitespace3(self):
        client = self.get_client()
        
        client.send_cmd("NICK      user1")
        client.send_cmd("USER   user1  *  *  :User One")
        
        self.get_reply(client, expect_code = replies.RPL_WELCOME, expect_nick="user1", expect_nparams = 1)

    @score(category="ROBUST")
    def test_whitespace4(self):
        client = self.get_client()
        
        client.send_cmd("  NICK      user1  ")
        client.send_cmd("  USER user1     *     *     :User One    ")
        
        self.get_reply(client, expect_code = replies.RPL_WELCOME, expect_nick="user1", expect_nparams = 1)

    @score(category="ROBUST")
    def test_whitespace5(self):
        client1 = self._connect_user("user1", "User One")

        client1.send_cmd("  ")

        self.assertRaises(ReplyTimeoutException, self.get_reply, client1)   

        
    def _gen_long_msg(self, length):
        msg = ""
        for i in range(length):
            msg += chr(97 + (i % 26))
        return msg
        
    @score(category="ROBUST")
    def test_length1(self):
        client1 = self._connect_user("user1", "User One")
        client2 = self._connect_user("user2", "User Two")
        
        base = "PRIVMSG user2 :"
        
        truncated_msg = self._gen_long_msg(510 - len(base))
        
        msg = self._gen_long_msg(512 - len(base))
        client1.send_cmd(base + msg)
        self._test_relayed_privmsg(client2, from_nick="user1", recip="user2", msg=truncated_msg)                  

        self.assertRaises(ReplyTimeoutException, self.get_reply, client1)   

    @score(category="ROBUST")
    def test_length2(self):
        client1 = self._connect_user("user1", "User One")
        client2 = self._connect_user("user2", "User Two")
        
        base = "PRIVMSG user2 :"
        
        truncated_msg = self._gen_long_msg(510 - len(base))
        
        msg = self._gen_long_msg(2048 - len(base))
        client1.send_cmd(base + msg)
        self._test_relayed_privmsg(client2, from_nick="user1", recip="user2", msg=truncated_msg)                  

        self.assertRaises(ReplyTimeoutException, self.get_reply, client1)   

    @score(category="ROBUST")
    def test_length3(self):
        client1 = self._connect_user("user1", "User One")
        client2 = self._connect_user("user2", "User Two")
        
        base = "PRIVMSG user2 :"
        
        truncated_msg = self._gen_long_msg(510 - len(base))
        
        msg = self._gen_long_msg(512 - len(base))
        client1.send_cmd(base + msg)
        self._test_relayed_privmsg(client2, from_nick="user1", recip="user2", msg=truncated_msg)                  

        client1.send_cmd(base + msg)
        self._test_relayed_privmsg(client2, from_nick="user1", recip="user2", msg=truncated_msg)                  

    @score(category="ROBUST")
    def test_length4(self):
        client1 = self._connect_user("user1", "User One")
        client2 = self._connect_user("user2", "User Two")
        
        base = "PRIVMSG user2 :"
        
        truncated_msg = self._gen_long_msg(510 - len(base))
        
        for i in (510,511,512,513,514,515):
            msg = self._gen_long_msg(i - len(base))
            client1.send_cmd(base + msg)
            self._test_relayed_privmsg(client2, from_nick="user1", recip="user2", msg=truncated_msg)                  

import tests.replies as replies
import time
from tests.common import ChircTestCase, ChircClient
from tests.scores import score

class UnknownCommands(ChircTestCase):

    @score(category="ERR_UNKNOWN")
    def test_unknown1(self):
        client1 = self._connect_user("user1", "User One")
        
        client1.send_cmd("VERSION")
        
        reply = self.get_reply(client1, expect_code = replies.ERR_UNKNOWNCOMMAND, expect_nick = "user1", 
                               expect_nparams = 2, expect_short_params = ["VERSION"],
                               long_param_re = "Unknown command")             
        
        
    @score(category="ERR_UNKNOWN")
    def test_unknown2(self):
        client1 = self._connect_user("user1", "User One")
        
        client1.send_cmd("WHOWAS user2")
        
        reply = self.get_reply(client1, expect_code = replies.ERR_UNKNOWNCOMMAND, expect_nick = "user1", 
                               expect_nparams = 2, expect_short_params = ["WHOWAS"],
                               long_param_re = "Unknown command")            


    @score(category="ERR_UNKNOWN")
    def test_unknown3(self):
        client1 = self._connect_user("user1", "User One")
        
        client1.send_cmd("KILL user2 :Bad user")
        
        reply = self.get_reply(client1, expect_code = replies.ERR_UNKNOWNCOMMAND, expect_nick = "user1", 
                               expect_nparams = 2, expect_short_params = ["KILL"],
                               long_param_re = "Unknown command")    
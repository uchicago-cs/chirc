import tests.replies as replies
import time
from tests.common import ChircTestCase, ChircClient
from tests.scores import score

class WHOIS(ChircTestCase):

    @score(category="WHOIS")
    def test_whois(self):
        client1 = self._connect_user("user1", "User One")
        client2 = self._connect_user("user2", "User Two")
        
        client1.send_cmd("WHOIS user2")
        
        reply = self.get_reply(client1, expect_code = replies.RPL_WHOISUSER, 
                               expect_nparams = 5, long_param_re = "User Two")    
        
        reply = self.get_reply(client1, expect_code = replies.RPL_WHOISSERVER, 
                               expect_nparams = 3)    

        reply = self.get_reply(client1, expect_code = replies.RPL_ENDOFWHOIS, 
                               expect_nparams = 2, long_param_re = "End of WHOIS list")    
        
        
    @score(category="WHOIS")
    def test_whois_nonick(self):
        client1 = self._connect_user("user1", "User One")
        
        client1.send_cmd("WHOIS user2")
        
        reply = self.get_reply(client1, expect_code = replies.ERR_NOSUCHNICK, expect_nick = "user1", 
                               expect_nparams = 2, expect_short_params = ["user2"],
                               long_param_re = "No such nick/channel")             
        
        
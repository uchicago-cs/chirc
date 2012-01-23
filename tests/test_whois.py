import tests.replies as replies
import time
from tests.common import ChircTestCase, ChircClient
from tests.common import channels1, channels2, channels3, channels4
from tests.scores import score

class WHOIS(ChircTestCase):

    @score(category="WHOIS")
    def test_whois1(self):
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
        
    def _test_userchannels(self, channels, nick, channelstring):
        whois_channels = channelstring[0:-1].split()
        for qchannel in whois_channels:
            if qchannel[0] in ('@', '+'):
                modchar = qchannel[0]
                channel = qchannel[1:]
            else:
                modchar = ""
                channel = qchannel
                
            users = channels[channel]
            
            self.assertIn(modchar + nick, users, "RPL_WHOISCHANNELS: Expected %s to be in %s (for channels '%s')" % (modchar + nick, channel, channelstring))
        
    @score(category="UPDATE_1B")
    def test_whois2(self):
        users = self._channels_connect(channels3) 

        users["user1"].send_cmd("WHOIS user2")
        
        reply = self.get_reply(users["user1"], expect_code = replies.RPL_WHOISUSER, 
                               expect_nparams = 5, long_param_re = "user2")    

        reply = self.get_reply(users["user1"], expect_code = replies.RPL_WHOISCHANNELS, 
                               expect_nparams = 2) 
        self._test_userchannels(channels3, "user2", reply.params[2][1:])        
        
        reply = self.get_reply(users["user1"], expect_code = replies.RPL_WHOISSERVER, 
                               expect_nparams = 3) 

        reply = self.get_reply(users["user1"], expect_code = replies.RPL_ENDOFWHOIS, 
                           expect_nparams = 2, long_param_re = "End of WHOIS list")           
        
    @score(category="UPDATE_1B")
    def test_whois3(self):
        users = self._channels_connect(channels3, aways=["user8"], ircops=["user8"]) 

        users["user1"].send_cmd("WHOIS user8")
        
        reply = self.get_reply(users["user1"], expect_code = replies.RPL_WHOISUSER, 
                               expect_nparams = 5, long_param_re = "user8")    

        reply = self.get_reply(users["user1"], expect_code = replies.RPL_WHOISCHANNELS, 
                               expect_nparams = 2) 
        self._test_userchannels(channels3, "user8", reply.params[2][1:])        
        
        reply = self.get_reply(users["user1"], expect_code = replies.RPL_WHOISSERVER, 
                               expect_nparams = 3) 
        
        reply = self.get_reply(users["user1"], expect_code = replies.RPL_AWAY, expect_nick = "user1",
                               expect_nparams = 2, expect_short_params = ["user8"],
                               long_param_re = "I'm away")     
        
        reply = self.get_reply(users["user1"], expect_code = replies.RPL_WHOISOPERATOR, 
                               expect_nparams = 2, expect_short_params = ["user8"],
                               long_param_re = "is an IRC operator")                 

        reply = self.get_reply(users["user1"], expect_code = replies.RPL_ENDOFWHOIS, 
                           expect_nparams = 2, long_param_re = "End of WHOIS list")           
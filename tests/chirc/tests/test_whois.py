import pytest

from chirc import replies
import chirc.tests.fixtures as fixtures

class TestWHOIS(object):

    @pytest.mark.category("WHOIS")
    def test_whois1(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        client2 = irc_session.connect_user("user2", "User Two")
        
        client1.send_cmd("WHOIS user2")
        
        reply = irc_session.get_reply(client1, expect_code = replies.RPL_WHOISUSER, 
                               expect_nparams = 5, long_param_re = "User Two")    
        
        reply = irc_session.get_reply(client1, expect_code = replies.RPL_WHOISSERVER, 
                               expect_nparams = 3)    

        reply = irc_session.get_reply(client1, expect_code = replies.RPL_ENDOFWHOIS, 
                           expect_nparams = 2, long_param_re = "End of WHOIS list")    
        
        
    @pytest.mark.category("WHOIS")
    def test_whois_nonick(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("WHOIS user2")
        
        reply = irc_session.get_reply(client1, expect_code = replies.ERR_NOSUCHNICK, expect_nick = "user1", 
                               expect_nparams = 2, expect_short_params = ["user2"],
                               long_param_re = "No such nick/channel")             
        
    def _test_userchannels(self, irc_session, channels, nick, channelstring):
        whois_channels = channelstring[0:-1].split()
        for qchannel in whois_channels:
            if qchannel[0] in ('@', '+'):
                modchar = qchannel[0]
                channel = qchannel[1:]
            else:
                modchar = ""
                channel = qchannel
                
            users = channels[channel]

            assert modchar + nick in users, "RPL_WHOISCHANNELS: Expected {} to be in {} (for channels '{}')".format(modchar + nick, channel, channelstring)            
        
    @pytest.mark.category("UPDATE_1B")
    def test_whois2(self, irc_session):
        users = irc_session.connect_and_join_channels(fixtures.channels3) 

        users["user1"].send_cmd("WHOIS user2")
        
        reply = irc_session.get_reply(users["user1"], expect_code = replies.RPL_WHOISUSER, 
                               expect_nparams = 5, long_param_re = "user2")    

        reply = irc_session.get_reply(users["user1"], expect_code = replies.RPL_WHOISCHANNELS, 
                               expect_nparams = 2) 
        
        self._test_userchannels(irc_session, fixtures.channels3, "user2", reply.params[2][1:])        
        
        reply = irc_session.get_reply(users["user1"], expect_code = replies.RPL_WHOISSERVER, 
                               expect_nparams = 3) 

        reply = irc_session.get_reply(users["user1"], expect_code = replies.RPL_ENDOFWHOIS, 
                           expect_nparams = 2, long_param_re = "End of WHOIS list")           
        
    @pytest.mark.category("UPDATE_1B")
    def test_whois3(self, irc_session):
        users = irc_session.connect_and_join_channels(fixtures.channels3, aways=["user8"], ircops=["user8"]) 

        users["user1"].send_cmd("WHOIS user8")
        
        reply = irc_session.get_reply(users["user1"], expect_code = replies.RPL_WHOISUSER, 
                               expect_nparams = 5, long_param_re = "user8")    

        reply = irc_session.get_reply(users["user1"], expect_code = replies.RPL_WHOISCHANNELS, 
                               expect_nparams = 2) 
        
        self._test_userchannels(irc_session, fixtures.channels3, "user8", reply.params[2][1:])        
        
        reply = irc_session.get_reply(users["user1"], expect_code = replies.RPL_WHOISSERVER, 
                               expect_nparams = 3) 
        
        reply = irc_session.get_reply(users["user1"], expect_code = replies.RPL_AWAY, expect_nick = "user1",
                               expect_nparams = 2, expect_short_params = ["user8"],
                               long_param_re = "I'm away")     
        
        reply = irc_session.get_reply(users["user1"], expect_code = replies.RPL_WHOISOPERATOR, 
                               expect_nparams = 2, expect_short_params = ["user8"],
                               long_param_re = "is an IRC operator")                 

        reply = irc_session.get_reply(users["user1"], expect_code = replies.RPL_ENDOFWHOIS, 
                           expect_nparams = 2, long_param_re = "End of WHOIS list")           
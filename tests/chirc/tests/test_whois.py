import pytest

from chirc import replies
import chirc.tests.fixtures as fixtures

class TestWHOIS(object):

    @pytest.mark.category("WHOIS")
    def test_whois1(self, irc_session):
        """
        Test doing a WHOIS on a user (user2) that is not in any channels.
        """
        
        
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
        """
        Test doing a WHOIS on a user (user2) that does not exist in the server.
        """
        
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("WHOIS user2")
        
        reply = irc_session.get_reply(client1, expect_code = replies.ERR_NOSUCHNICK, expect_nick = "user1", 
                               expect_nparams = 2, expect_short_params = ["user2"],
                               long_param_re = "No such nick/channel")             
        
        
    @pytest.mark.category("WHOIS")
    def test_whois_params(self, irc_session):
        """
        Test sending a WHOIS without parameters..
        """
        
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("WHOIS")

        irc_session.get_reply(client1, expect_timeout = True)              
        
    def _test_userchannels(self, irc_session, channels, nick, channelstring):        
        whois_channels = channelstring.strip().split()
        for qchannel in whois_channels:
            if qchannel[0] in ('@', '+'):
                modchar = qchannel[0]
                channel = qchannel[1:]
            else:
                modchar = ""
                channel = qchannel
                
            assert channel in channels, "RPL_WHOISCHANNELS: Includes unexpected channel {}".format(channel)
                
            users = channels[channel]
            
            assert modchar + nick in users, "RPL_WHOISCHANNELS: Expected {} to be in {} (for channels '{}')".format(modchar + nick, channel, channelstring)
        
        if channelstring[-1] != " ":
            pytest.fail("You may want to *very carefully* reread the specification for RPL_WHOISCHANNELS...")
        
        
    @pytest.mark.category("UPDATE_ASSIGNMENT2")
    def test_whois2(self, irc_session):
        """
        Given the following users and channels (@ denotes channel
        operators, and + denotes a user with voice privileges):
        
        #test1: @user1, user2, user3
        #test2: @user2
        #test3: @user3, @user4, user5, user6
        #test4: @user7, +user8, +user9, user1, user2
        #test5: @user1, @user5 
        
        Not in a channel: user10, user11             
        
        Test doing a WHOIS on user2
        """
        
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
        
    @pytest.mark.category("UPDATE_ASSIGNMENT2")
    def test_whois3(self, irc_session):
        """
        Given the following users and channels (@ denotes channel
        operators, and + denotes a user with voice privileges):
        
        #test1: @user1, user2, user3
        #test2: @user2
        #test3: @user3, @user4, user5, user6
        #test4: @user7, +user8, +user9, user1, user2
        #test5: @user1, @user5 
        
        Not in a channel: user10, user11             
        
        Where, additionally, user8 is an IRCop and is away.
        
        Test doing a WHOIS on user8
        """
                
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
        
        
            

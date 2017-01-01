import pytest
from chirc import replies

@pytest.mark.category("ERR_UNKNOWN")
class TestUnknownCommands(object):

    def test_unknown1(self, irc_session):
        """
        Test sending an unknown command.
        """
        
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("VERSION")
        
        reply = irc_session.get_reply(client1, expect_code = replies.ERR_UNKNOWNCOMMAND, expect_nick = "user1", 
                                      expect_nparams = 2, expect_short_params = ["VERSION"],
                                      long_param_re = "Unknown command")             
        
        
    def test_unknown2(self, irc_session):
        """
        Test sending an unknown command.
        """

        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("WHOWAS user2")
        
        reply = irc_session.get_reply(client1, expect_code = replies.ERR_UNKNOWNCOMMAND, expect_nick = "user1", 
                                      expect_nparams = 2, expect_short_params = ["WHOWAS"],
                                      long_param_re = "Unknown command")            


    def test_unknown3(self, irc_session):
        """
        Test sending an unknown command.
        """
        
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("KILL user2 :Bad user")
        
        reply = irc_session.get_reply(client1, expect_code = replies.ERR_UNKNOWNCOMMAND, expect_nick = "user1", 
                                      expect_nparams = 2, expect_short_params = ["KILL"],
                                      long_param_re = "Unknown command")    
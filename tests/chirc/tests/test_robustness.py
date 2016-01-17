import pytest
from chirc import replies
from chirc.types import ReplyTimeoutException

@pytest.mark.category("ROBUST")
class TestRobustness(object):

    def test_whitespace1(self, irc_session):
        client = irc_session.get_client()
        
        client.send_cmd("  ")
        
        with pytest.raises(ReplyTimeoutException):
            irc_session.get_reply(client)            
        
    def test_whitespace2(self, irc_session):
        client = irc_session.get_client()
        
        client.send_cmd(" NICK user1 ")
        client.send_cmd(" USER user1 * * :User One ")
        
        irc_session.get_reply(client, expect_code = replies.RPL_WELCOME, expect_nick="user1", expect_nparams = 1)

    def test_whitespace3(self, irc_session):
        client = irc_session.get_client()
        
        client.send_cmd("NICK      user1")
        client.send_cmd("USER   user1  *  *  :User One")
        
        irc_session.get_reply(client, expect_code = replies.RPL_WELCOME, expect_nick="user1", expect_nparams = 1)

    def test_whitespace4(self, irc_session):
        client = irc_session.get_client()
        
        client.send_cmd("  NICK      user1  ")
        client.send_cmd("  USER user1     *     *     :User One    ")
        
        irc_session.get_reply(client, expect_code = replies.RPL_WELCOME, expect_nick="user1", expect_nparams = 1)

    def test_whitespace5(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")

        client1.send_cmd("  ")

        with pytest.raises(ReplyTimeoutException):
            irc_session.get_reply(client1)   

        
    def _gen_long_msg(self, length):
        msg = ""
        for i in range(length):
            msg += chr(97 + (i % 26))
        return msg
        
    def test_length1(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        client2 = irc_session.connect_user("user2", "User Two")
        
        base = "PRIVMSG user2 :"
        
        msg = self._gen_long_msg(512 - len(base))
        client1.send_cmd(base + msg)
        privmsg = irc_session.get_message(client2, expect_prefix = True, expect_cmd = "PRIVMSG", 
                                          expect_nparams = 2, expect_short_params = ["user2"])
        assert len(privmsg.raw()) == 510
        relayed_msg = privmsg.params[-1]
        assert relayed_msg[0] == ":"
        assert msg.startswith(relayed_msg[1:])               

        with pytest.raises(ReplyTimeoutException):
            irc_session.get_reply(client1)   

    def test_length2(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        client2 = irc_session.connect_user("user2", "User Two")
        
        base = "PRIVMSG user2 :"
                
        msg = self._gen_long_msg(2048 - len(base))
        client1.send_cmd(base + msg)
        privmsg = irc_session.get_message(client2, expect_prefix = True, expect_cmd = "PRIVMSG", 
                                          expect_nparams = 2, expect_short_params = ["user2"])
        assert len(privmsg.raw()) == 510
        relayed_msg = privmsg.params[-1]
        assert relayed_msg[0] == ":"
        assert msg.startswith(relayed_msg[1:])               

        with pytest.raises(ReplyTimeoutException):
            irc_session.get_reply(client1)   

    def test_length3(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        client2 = irc_session.connect_user("user2", "User Two")
        
        base = "PRIVMSG user2 :"
        
        
        msg = self._gen_long_msg(512 - len(base))
        client1.send_cmd(base + msg)
        privmsg = irc_session.get_message(client2, expect_prefix = True, expect_cmd = "PRIVMSG", 
                                          expect_nparams = 2, expect_short_params = ["user2"])
        assert len(privmsg.raw()) == 510
        relayed_msg = privmsg.params[-1]
        assert relayed_msg[0] == ":"
        assert msg.startswith(relayed_msg[1:])               

        client1.send_cmd(base + msg)
        privmsg = irc_session.get_message(client2, expect_prefix = True, expect_cmd = "PRIVMSG", 
                                          expect_nparams = 2, expect_short_params = ["user2"])
        assert len(privmsg.raw()) == 510
        relayed_msg = privmsg.params[-1]
        assert relayed_msg[0] == ":"
        assert msg.startswith(relayed_msg[1:])               

    def test_length4(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        client2 = irc_session.connect_user("user2", "User Two")
        
        base = "PRIVMSG user2 :"
        
        for i in (510,511,512,513,514,515):
            msg = self._gen_long_msg(i - len(base))
            client1.send_cmd(base + msg)
            privmsg = irc_session.get_message(client2, expect_prefix = True, expect_cmd = "PRIVMSG", 
                                              expect_nparams = 2, expect_short_params = ["user2"])
            assert len(privmsg.raw()) == 510
            relayed_msg = privmsg.params[-1]
            assert relayed_msg[0] == ":"
            assert msg.startswith(relayed_msg[1:])               


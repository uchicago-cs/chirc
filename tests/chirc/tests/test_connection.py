import chirc.replies as replies
import pytest
from chirc.types import ReplyTimeoutException

@pytest.mark.category("BASIC_CONNECTION")
class TestBasicConnection(object):

    def test_connect_simple(self, irc_session):
        client = irc_session.get_client(nodelay = True)
        
        client.send_raw(["NICK user1\r\n", 
                         "USER user1 * * :User One\r\n"],
                        wait=0.05)
        
        irc_session.get_reply(client, expect_code = replies.RPL_WELCOME, expect_nick="user1", expect_nparams = 1,
                              long_param_re= "Welcome to the Internet Relay Network user1!user1@.*")

    def test_connect_both_messages_at_once(self, irc_session):
        client = irc_session.get_client(nodelay = True)
        
        client.send_raw("NICK user1\r\nUSER user1 * * :User One\r\n")
        
        irc_session.get_reply(client, expect_code = replies.RPL_WELCOME, expect_nick="user1", expect_nparams = 1)

    def test_connect_partitioned_messages1(self, irc_session):
        client = irc_session.get_client(nodelay = True)
        
        client.send_raw(["NICK ", 
                         "user1\r\nUSER user1 * * :User One\r\n"],
                        wait=0.05)
        
        irc_session.get_reply(client, expect_code = replies.RPL_WELCOME, expect_nick="user1", expect_nparams = 1)

    def test_connect_partitioned_messages2(self, irc_session):
        client = irc_session.get_client(nodelay = True)
        
        client.send_raw(["NICK user1\r\nUSER user1 "
                         "* * :User One\r\n"],
                        wait=0.05)
        
        irc_session.get_reply(client, expect_code = replies.RPL_WELCOME, expect_nick="user1", expect_nparams = 1)

    def test_connect_partitioned_messages3(self, irc_session):
        client = irc_session.get_client(nodelay = True)
        
        client.send_raw(["NICK user1", 
                         "\r\nUSER user1 * * :User One\r\n"],
                        wait=0.05)
        
        irc_session.get_reply(client, expect_code = replies.RPL_WELCOME, expect_nick="user1", expect_nparams = 1)

    def test_connect_partitioned_messages4(self, irc_session):
        client = irc_session.get_client(nodelay = True)
        
        client.send_raw(["NICK user1\r\nUSER user1 * * :User One",
                         "\r\n"],
                        wait=0.05)
        
        irc_session.get_reply(client, expect_code = replies.RPL_WELCOME, expect_nick="user1", expect_nparams = 1)

    def test_connect_partitioned_messages5(self, irc_session):
        client = irc_session.get_client(nodelay = True)
        
        client.send_raw(["NICK user1",
                         "\r\n", 
                         "USER user1 * * :User One",
                         "\r\n"],
                        wait=0.05)
        
        irc_session.get_reply(client, expect_code = replies.RPL_WELCOME, expect_nick="user1", expect_nparams = 1)

    def test_connect_partitioned_messages6(self, irc_session):
        client = irc_session.get_client(nodelay = True)
        
        client.send_raw(["NICK user1\r",
                         "\nUSER ", 
                         "user1 * * ",
                         ":User One\r",
                         "\n"],
                        wait=0.05)        

    def test_connect_partitioned_messages7(self, irc_session):
        client = irc_session.get_client(nodelay = True)        
        
        client.send_raw(["NI",
                         "CK ",
                         "user1\r",
                         "\n",
                         "USER user",
                         "1 * * ",
                         ":Us",
                         "er ",
                         "One",
                         "\r",
                         "\n"],
                        wait=0.05)
        
        irc_session.get_reply(client, expect_code = replies.RPL_WELCOME, expect_nick="user1", expect_nparams = 1)

    def test_connect_nick_user_parsing1(self, irc_session):
        client = irc_session.get_client(nodelay = True)
        
        client.send_raw(["NICK nick42\r\n", 
                         "USER user42 * * :User Forty Two\r\n"],
                        wait=0.05)
        
        irc_session.get_reply(client, expect_code = replies.RPL_WELCOME, expect_nick="nick42", expect_nparams = 1,
                              long_param_re= "Welcome to the Internet Relay Network nick42!user42@.*")

    def test_connect_nick_user_parsing2(self, irc_session):
        client = irc_session.get_client(nodelay = True)
        
        client.send_raw(["NICK nick4", 
                         "2\r\n", 
                         "USER user4",
                         "2 * * :User Forty Two\r\n"],
                        wait=0.05)
        
        irc_session.get_reply(client, expect_code = replies.RPL_WELCOME, expect_nick="nick42", expect_nparams = 1,
                              long_param_re= "Welcome to the Internet Relay Network nick42!user42@.*")
        
    def test_connect_nick_user_parsing3(self, irc_session):
        client = irc_session.get_client(nodelay = True)
        
        client.send_raw(["NICK nick4", 
                         "2",
                         "4",
                         "2",
                         "\r\n", 
                         "USER user4",
                         "2",
                         "4",
                         "2",
                         " * * :User Four Thousand Two Hundred and Forty Two\r\n"],
                        wait=0.05)
        
        irc_session.get_reply(client, expect_code = replies.RPL_WELCOME, expect_nick="nick4242", expect_nparams = 1,
                              long_param_re= "Welcome to the Internet Relay Network nick4242!user4242@.*")        

    def test_connect_no_unexpected_welcome1(self, irc_session):
        client = irc_session.get_client(nodelay = True)
        
        client.send_raw("NICK user1\r\n")

        with pytest.raises(ReplyTimeoutException):
            irc_session.get_reply(client, expect_code = replies.RPL_WELCOME, expect_nick="user1", expect_nparams = 1)
            
    def test_connect_no_unexpected_welcome2(self, irc_session):
        client = irc_session.get_client(nodelay = True)
        
        client.send_raw("USER user1 * * :User One\r\n")

        with pytest.raises(ReplyTimeoutException):
            irc_session.get_reply(client, expect_code = replies.RPL_WELCOME, expect_nick="user1", expect_nparams = 1)  
            
    def test_connect_no_unexpected_welcome3(self, irc_session):
        client = irc_session.get_client(nodelay = True)
        
        client.send_raw(["NICK user1\r\n",
                         "USER user1 * * :User One"],
                        wait=0.05)

        with pytest.raises(ReplyTimeoutException):
            irc_session.get_reply(client, expect_code = replies.RPL_WELCOME, expect_nick="user1", expect_nparams = 1)                       
            

@pytest.mark.category("CONNECTION_REGISTRATION")
class TestFullConnection(object):

    def test_connect_full1(self, irc_session):
        client = irc_session.get_client()
        
        client.send_cmd("NICK user1")
        client.send_cmd("USER user1 * * :User One")
        
        irc_session.verify_welcome_messages(client, "user1")   
        
    def test_connect_full2(self, irc_session):
        client = irc_session.get_client()
        
        client.send_cmd("USER user1 * * :User One")
        client.send_cmd("NICK user1")
        
        irc_session.verify_welcome_messages(client, "user1")           

    def test_connect_full3(self, irc_session):
        client = irc_session.get_client()
        
        client.send_cmd("NICK user1")
        client.send_cmd("USER user1 * * :User One")
        
        irc_session.verify_welcome_messages(client, "user1")
        irc_session.verify_lusers(client, "user1")
        irc_session.verify_motd(client, "user1")        


@pytest.mark.category("CONNECTION_REGISTRATION")
class TestMultiuserConnection(object):        
        
    def test_connect_2users(self, irc_session):      
        irc_session.connect_user("user1", "User One")
        irc_session.connect_user("user2", "User Two")

    def test_connect_duplicate_nick(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")

        client2 = irc_session.get_client()
        client2.send_cmd("NICK user1")
        reply = irc_session.get_reply(client2, expect_code = replies.ERR_NICKNAMEINUSE, expect_nick = "*", expect_nparams = 2,
                                      expect_short_params = ["user1"],
                                      long_param_re = "Nickname is already in use")                
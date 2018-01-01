import chirc.replies as replies
import pytest
from chirc.types import ReplyTimeoutException

@pytest.mark.category("BASIC_CONNECTION")
class TestBasicConnection(object):

    def test_connect_simple1(self, irc_session):
        """
        Sends a NICK command followed by a USER command, and expects 
        to receive, at least, a RPL_WELCOME reply.
        """
        
        client = irc_session.get_client(nodelay = True)
        
        client.send_raw(["NICK user1\r\n", 
                         "USER user1 * * :User One\r\n"],
                        wait=0.05)
        
        irc_session.get_reply(client, expect_code = replies.RPL_WELCOME, expect_nick="user1", expect_nparams = 1,
                              long_param_re= "Welcome to the Internet Relay Network user1!user1@.*")

    def test_connect_simple2(self, irc_session):
        """
        Sends a USER command followed by a NICK command, and expects 
        to receive, at least, a RPL_WELCOME reply.
        """
                
        client = irc_session.get_client(nodelay = True)
        
        client.send_raw(["USER user1 * * :User One\r\n",
                         "NICK user1\r\n"],
                        wait=0.05)
        
        irc_session.get_reply(client, expect_code = replies.RPL_WELCOME, expect_nick="user1", expect_nparams = 1,
                              long_param_re= "Welcome to the Internet Relay Network user1!user1@.*")


    def test_connect_both_messages_at_once(self, irc_session):
        """
        Sends a NICK and USER command in the same TCP packet. This tests that
        the server doesn't (incorrectly) assume that calling recv() will always
        return a single message.
        
        Note: TCP will sometimes do whatever TCP wants, which means this message
        could get partitioned.
        """
              
        client = irc_session.get_client(nodelay = True)
        
        client.send_raw("NICK user1\r\nUSER user1 * * :User One\r\n")
        
        irc_session.get_reply(client, expect_code = replies.RPL_WELCOME, expect_nick="user1", expect_nparams = 1)

    def test_connect_partitioned_messages1(self, irc_session):
        """
        Sends a NICK and USER command, but partitioned at a point other than
        at the \r\n terminator.
        
        Note: TCP will sometimes do whatever TCP wants, which means this message
        could get partitioned in other ways.        
        """        
        
        client = irc_session.get_client(nodelay = True)
        
        client.send_raw(["NICK ", 
                         "user1\r\nUSER user1 * * :User One\r\n"],
                        wait=0.05)
        
        irc_session.get_reply(client, expect_code = replies.RPL_WELCOME, expect_nick="user1", expect_nparams = 1)

    def test_connect_partitioned_messages2(self, irc_session):
        """
        Sends a NICK and USER command, but partitioned at a point other than
        at the \r\n terminator.
        
        Note: TCP will sometimes do whatever TCP wants, which means this message
        could get partitioned in other ways.        
        """        

        client = irc_session.get_client(nodelay = True)
        
        client.send_raw(["NICK user1\r\nUSER user1 ",
                         "* * :User One\r\n"],
                        wait=0.05)
        
        irc_session.get_reply(client, expect_code = replies.RPL_WELCOME, expect_nick="user1", expect_nparams = 1)

    def test_connect_partitioned_messages3(self, irc_session):
        """
        Sends a NICK and USER command, but partitioned at a point other than
        at the \r\n terminator.
        
        Note: TCP will sometimes do whatever TCP wants, which means this message
        could get partitioned in other ways.        
        """        

        client = irc_session.get_client(nodelay = True)
        
        client.send_raw(["NICK user1", 
                         "\r\nUSER user1 * * :User One\r\n"],
                        wait=0.05)
        
        irc_session.get_reply(client, expect_code = replies.RPL_WELCOME, expect_nick="user1", expect_nparams = 1)

    def test_connect_partitioned_messages4(self, irc_session):
        """
        Sends a NICK and USER command, but partitioned at a point other than
        at the \r\n terminator.
        
        Note: TCP will sometimes do whatever TCP wants, which means this message
        could get partitioned in other ways.        
        """        

        client = irc_session.get_client(nodelay = True)
        
        client.send_raw(["NICK user1\r\nUSER user1 * * :User One",
                         "\r\n"],
                        wait=0.05)
        
        irc_session.get_reply(client, expect_code = replies.RPL_WELCOME, expect_nick="user1", expect_nparams = 1)

    def test_connect_partitioned_messages5(self, irc_session):
        """
        Sends a NICK and USER command, but partitioned at a point other than
        at the \r\n terminator.
        
        Note: TCP will sometimes do whatever TCP wants, which means this message
        could get partitioned in other ways.        
        """        

        client = irc_session.get_client(nodelay = True)
        
        client.send_raw(["NICK user1",
                         "\r\n", 
                         "USER user1 * * :User One",
                         "\r\n"],
                        wait=0.05)
        
        irc_session.get_reply(client, expect_code = replies.RPL_WELCOME, expect_nick="user1", expect_nparams = 1)

    def test_connect_partitioned_messages6(self, irc_session):
        """
        Sends a NICK and USER command, but partitioned at a point other than
        at the \r\n terminator.
        
        Note: TCP will sometimes do whatever TCP wants, which means this message
        could get partitioned in other ways.        
        """        
        
        client = irc_session.get_client(nodelay = True)
        
        client.send_raw(["NICK user1\r",
                         "\nUSER ", 
                         "user1 * * ",
                         ":User One\r",
                         "\n"],
                        wait=0.05)        

    def test_connect_partitioned_messages7(self, irc_session):
        """
        Sends a NICK and USER command, but partitioned at a point other than
        at the \r\n terminator.
        
        Note: TCP will sometimes do whatever TCP wants, which means this message
        could get partitioned in other ways.        
        """        
        
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
        """
        Tests that the server is actually parsing the NICK and USER parameters
        (as opposed to just hardcoding "nick1" and "user1" which is used in
        other tests.       
        """        
        
        client = irc_session.get_client(nodelay = True)
        
        client.send_raw(["NICK nick42\r\n", 
                         "USER user42 * * :User Forty Two\r\n"],
                        wait=0.05)
        
        irc_session.get_reply(client, expect_code = replies.RPL_WELCOME, expect_nick="nick42", expect_nparams = 1,
                              long_param_re= "Welcome to the Internet Relay Network nick42!user42@.*")

    def test_connect_nick_user_parsing2(self, irc_session):
        """
        Tests that the server is actually parsing the NICK and USER parameters
        (as opposed to just hardcoding "nick1" and "user1" which is used in
        other tests. Additionally, partitions the messages.       
        """     
                
        client = irc_session.get_client(nodelay = True)
        
        client.send_raw(["NICK nick4", 
                         "2\r\n", 
                         "USER user4",
                         "2 * * :User Forty Two\r\n"],
                        wait=0.05)
        
        irc_session.get_reply(client, expect_code = replies.RPL_WELCOME, expect_nick="nick42", expect_nparams = 1,
                              long_param_re= "Welcome to the Internet Relay Network nick42!user42@.*")
        
    def test_connect_nick_user_parsing3(self, irc_session):
        """
        Tests that the server is actually parsing the NICK and USER parameters
        (as opposed to just hardcoding "nick1" and "user1" which is used in
        other tests. Additionally, partitions the messages.       
        """     
                
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

    def test_connect_nick_user_parsing4(self, irc_session):
        """
        Tests that the server only uses the last NICK message sent during
        the registration phase.     
        """     
                
        client = irc_session.get_client(nodelay = True)
        
        client.send_raw(["NICK nick1\r\n",
                         "NICK nick2\r\n", 
                         "NICK nick3\r\n", 
                         "NICK nick42\r\n", 
                         "USER user42 * * :User Forty Two\r\n"],
                        wait=0.05)
        
        irc_session.get_reply(client, expect_code = replies.RPL_WELCOME, expect_nick="nick42", expect_nparams = 1,
                              long_param_re= "Welcome to the Internet Relay Network nick42!user42@.*")

    def test_connect_nick_user_parsing5(self, irc_session):
        """
        Tests that the server only uses the last USER message sent during
        the registration phase.     
        """     
                  
        client = irc_session.get_client(nodelay = True)
        
        client.send_raw(["USER user1 * * :User One\r\n",
                         "USER user2 * * :User Two\r\n",
                         "USER user3 * * :User Three\r\n",
                         "USER user42 * * :User Forty Two\r\n",
                         "NICK nick42\r\n", 
                         ],
                        wait=0.05)
        
        irc_session.get_reply(client, expect_code = replies.RPL_WELCOME, expect_nick="nick42", expect_nparams = 1,
                              long_param_re= "Welcome to the Internet Relay Network nick42!user42@.*")


    def test_connect_no_unexpected_welcome1(self, irc_session):
        """
        Tests that the RPL_WELCOME message isn't just being sent immediately
        after receiving a NICK command (without also receiving a USER command)     
        """     
                
        client = irc_session.get_client(nodelay = True)
        
        client.send_raw("NICK user1\r\n")

        irc_session.get_reply(client, expect_timeout = True)
            
    def test_connect_no_unexpected_welcome2(self, irc_session):
        """
        Tests that the RPL_WELCOME message isn't just being sent immediately
        after receiving a USER command (without also receiving a NICK command)     
        """     

        client = irc_session.get_client(nodelay = True)
        
        client.send_raw("USER user1 * * :User One\r\n")

        irc_session.get_reply(client, expect_timeout = True)
            
    def test_connect_no_unexpected_welcome3(self, irc_session):
        """
        Sends a NICK and USER command, but the USER command does not
        have a \r\n at the end. No RPL_WELCOME should be sent.    
        """     
                
        client = irc_session.get_client(nodelay = True)
        
        client.send_raw(["NICK user1\r\n",
                         "USER user1 * * :User One"],
                        wait=0.05)

        irc_session.get_reply(client, expect_timeout = True)

    def test_connect_no_unexpected_welcome4(self, irc_session):
        """
        Sends two USER commands, but no NICK, so no RPL_WELCOME should be sent. 
        (tests that the server isn't just unconditionally sending the welcome
        messages after receiving two messages)    
        """             
        
        client = irc_session.get_client(nodelay = True)
        
        client.send_raw(["USER user1 * * :User One\r\n",
                         "USER user2 * * :User Two\r\n"],
                        wait=0.05)

        irc_session.get_reply(client, expect_timeout = True)
            
    def test_connect_no_unexpected_welcome5(self, irc_session):
        """
        Sends two NICK commands, but no USER, so no RPL_WELCOME should be sent. 
        (tests that the server isn't just unconditionally sending the welcome
        messages after receiving two messages)    
        """             
        
        client = irc_session.get_client(nodelay = True)
        
        client.send_raw(["NICK user1\r\n",
                         "NICK user2\r\n"],
                        wait=0.05)

        irc_session.get_reply(client, expect_timeout = True)

    def test_connect_no_unexpected_welcome6(self, irc_session):
        """
        Sends multiple USER commands, but no NICK. No RPL_WELCOME should be sent.   
        """             
        
        client = irc_session.get_client(nodelay = True)
        
        client.send_raw(["USER user1 * * :User One\r\n",
                         "USER user2 * * :User Two\r\n",
                         "USER user3 * * :User Two\r\n",
                         "USER user4 * * :User Two\r\n",
                         "USER user5 * * :User Two\r\n",],
                        wait=0.05)

        irc_session.get_reply(client, expect_timeout = True)

    def test_connect_no_unexpected_welcome7(self, irc_session):
        """
        Sends multiple NICK commands, but no USER. No RPL_WELCOME should be sent.   
        """   
                
        client = irc_session.get_client(nodelay = True)
        
        client.send_raw(["NICK user1\r\n",
                         "NICK user2\r\n",
                         "NICK user3\r\n",
                         "NICK user4\r\n",
                         "NICK user5\r\n"],
                        wait=0.05)

        irc_session.get_reply(client, expect_timeout = True)


@pytest.mark.category("CONNECTION_REGISTRATION")
class TestFullConnection(object):

    def test_connect_full1(self, irc_session):
        """
        Checks that all welcome messages are sent after the NICK and USER
        commands are received.    
        """          
        
        client = irc_session.get_client()
        
        client.send_cmd("NICK user1")
        client.send_cmd("USER user1 * * :User One")
        
        irc_session.verify_welcome_messages(client, "user1")   
        
    def test_connect_full2(self, irc_session):
        """
        Checks that all welcome messages are sent after the USER and NICK
        commands are received.    
        """          
        
        client = irc_session.get_client()
        
        client.send_cmd("USER user1 * * :User One")
        client.send_cmd("NICK user1")
        
        irc_session.verify_welcome_messages(client, "user1")           

    def test_connect_full3(self, irc_session):
        """
        Checks that all welcome messages, as well as the LUSERS and
        MOTD replies, are sent after the NICK and USER commands are received.    
        """     
                
        client = irc_session.get_client()
        
        client.send_cmd("NICK user1")
        client.send_cmd("USER user1 * * :User One")
        
        irc_session.verify_welcome_messages(client, "user1")
        irc_session.verify_lusers(client, "user1")
        irc_session.verify_motd(client, "user1")        
      

@pytest.mark.category("CONNECTION_REGISTRATION")
class TestConnectionNotRegistered(object):
 
 
    def test_connect_not_registered1(self, irc_session):
        """
        Checks that ERR_NOTREGISTERED is returned if a valid
        command is sent before registration is complete
        """     
                
        client = irc_session.get_client()
        
        client.send_cmd("PRIVMSG user2 :Hello")
        
        reply = irc_session.get_reply(client, expect_code = replies.ERR_NOTREGISTERED, 
                                      expect_nick = "*", expect_nparams = 1,
                                      long_param_re = "You have not registered")    

    def test_connect_not_registered2(self, irc_session):
        """
        Checks that ERR_NOTREGISTERED is returned if a valid
        command is sent before registration is complete
        """     
                
        client = irc_session.get_client()
        
        client.send_cmd("NICK user1")
        client.send_cmd("PRIVMSG user2 :Hello")
        
        reply = irc_session.get_reply(client, expect_code = replies.ERR_NOTREGISTERED, 
                                      expect_nick = "user1", expect_nparams = 1,
                                      long_param_re = "You have not registered")    

    def test_connect_not_registered3(self, irc_session):
        """
        Checks that ERR_NOTREGISTERED is returned if a valid
        command is sent before registration is complete
        """     
                
        client = irc_session.get_client()
        
        client.send_cmd("USER user1 * * :User One")
        client.send_cmd("PRIVMSG user2 :Hello")
        
        reply = irc_session.get_reply(client, expect_code = replies.ERR_NOTREGISTERED, 
                                      expect_nick = "*", expect_nparams = 1,
                                      long_param_re = "You have not registered")    
        
    def test_connect_not_registered4(self, irc_session):
        """
        Checks that an invalid command sent before registration is complete
        is just silently ignored.
        """     
                
        client = irc_session.get_client()
        
        client.send_cmd("NICK user1")        
        client.send_cmd("WHOWAS user2")
        
        irc_session.get_reply(client, expect_timeout = True)        

    def test_connect_not_registered5(self, irc_session):
        """
        Checks that an invalid command sent before registration is complete
        is just silently ignored.
        """     
                
        client = irc_session.get_client()
        
        client.send_cmd("WHOWAS user2")
        
        irc_session.get_reply(client, expect_timeout = True)    

    def test_connect_not_registered6(self, irc_session):
        """
        Checks that an invalid command sent before registration is complete
        is just silently ignored.
        """     
                
        client = irc_session.get_client()
        
        client.send_cmd("USER user1 * * :User One")        
        client.send_cmd("WHOWAS user2")
        
        irc_session.get_reply(client, expect_timeout = True)            

@pytest.mark.category("CONNECTION_REGISTRATION")
class TestConnectionParams(object):

    def test_params_NICK1(self, irc_session):
        """
        Checks that ERR_NONICKNAMEGIVEN is returned if no nickname
        is specified.   
        """     
                
        client = irc_session.get_client()
        
        client.send_cmd("NICK")
        
        reply = irc_session.get_reply(client, expect_code = replies.ERR_NONICKNAMEGIVEN, expect_nick = "*", expect_nparams = 1,
                                      long_param_re = "No nickname given")     
   
    def test_params_NICK2(self, irc_session):
        """
        Checks that ERR_NONICKNAMEGIVEN is returned if no nickname
        is specified (after sending USER)  
        """     
                
        client = irc_session.get_client()
        
        client.send_cmd("USER user1 * * :User One")        
        client.send_cmd("NICK")
        
        reply = irc_session.get_reply(client, expect_code = replies.ERR_NONICKNAMEGIVEN, expect_nick = "*", expect_nparams = 1,
                                      long_param_re = "No nickname given")     

    def test_params_USER1(self, irc_session):
        """
        Test ERR_NEEDMOREPARAMS reply during registration
        """
        
        client = irc_session.get_client()
        
        client.send_cmd("NICK user1")
        client.send_cmd("USER user1 * *")
        
        irc_session.get_ERR_NEEDMOREPARAMS_reply(client, 
                                                 expect_nick="user1", expect_cmd="USER")
        
    def test_params_USER2(self, irc_session):
        """
        Test ERR_NEEDMOREPARAMS reply during registration
        """
        
        client = irc_session.get_client()
        
        client.send_cmd("NICK user1")
        client.send_cmd("USER user1 *")
        
        irc_session.get_ERR_NEEDMOREPARAMS_reply(client, 
                                                 expect_nick="user1", expect_cmd="USER")
        
    def test_params_USER3(self, irc_session):
        """
        Test ERR_NEEDMOREPARAMS reply during registration
        """
        
        client = irc_session.get_client()
        
        client.send_cmd("NICK user1")
        client.send_cmd("USER user1")
        
        irc_session.get_ERR_NEEDMOREPARAMS_reply(client, 
                                                 expect_nick="user1", expect_cmd="USER")
        
    def test_params_USER4(self, irc_session):
        """
        Test ERR_NEEDMOREPARAMS reply during registration
        """
        
        client = irc_session.get_client()
        
        client.send_cmd("NICK user1")
        client.send_cmd("USER")
        
        irc_session.get_ERR_NEEDMOREPARAMS_reply(client, 
                                                 expect_nick="user1", expect_cmd="USER")

@pytest.mark.category("CONNECTION_REGISTRATION")
class TestMultiuserConnection(object):        
        
    def test_connect_2users(self, irc_session):      
        """
        Connects two clients to the server.    
        """     
                
        irc_session.connect_user("user1", "User One")
        irc_session.connect_user("user2", "User Two")

    def test_connect_duplicate_nick(self, irc_session):
        """
        Connects two clients to the server, but the second
        client tries to use the first client's nickname
        (and should get an ERR_NICKNAMEINUSE)    
        """     
        
        client1 = irc_session.connect_user("user1", "User One")

        client2 = irc_session.get_client()
        client2.send_cmd("NICK user1")
        reply = irc_session.get_reply(client2, expect_code = replies.ERR_NICKNAMEINUSE, expect_nick = "*", expect_nparams = 2,
                                      expect_short_params = ["user1"],
                                      long_param_re = "Nickname is already in use")     
        

@pytest.mark.category("CONNECTION_REGISTRATION")            
class TestQUIT(object):  
    
    def test_quit_after_registration1(self, irc_session):
        """
        Connects a client, and quits right after connecting.
        Verifies the ERROR response, but not whether the server
        actually disconnected the client.
        """
         
        client1 = irc_session.connect_user("user1", "User One")

        client1.send_cmd("QUIT :Goodbye!")

        irc_session.get_message(client1, expect_cmd = "ERROR", expect_nparams = 1,
                                long_param_re = "Closing Link: .* \(Goodbye!\)")

    def test_quit_after_registration2(self, irc_session):      
        """
        Connects a client, and quits right after connecting.
        Verifies the ERROR response and also checks whether the
        server disconnected the client.
        """

        client1 = irc_session.connect_user("user1", "User One")

        client1.send_cmd("QUIT :Goodbye!")

        irc_session.get_message(client1, expect_cmd = "ERROR", expect_nparams = 1,
                                long_param_re = "Closing Link: .* \(Goodbye!\)")      
        
        irc_session.verify_disconnect(client1)
        
    def test_quit_after_registration3(self, irc_session):      
        """
        Connects a client, and quits right after connecting.
        QUIT does not specify a message, so the default "Client Quit" should
        be assumed. Also verifies the ERROR response and also checks whether the
        server disconnected the client.
        """

        client1 = irc_session.connect_user("user1", "User One")

        client1.send_cmd("QUIT")

        irc_session.get_message(client1, expect_cmd = "ERROR", expect_nparams = 1,
                                long_param_re = "Closing Link: .* \(Client Quit\)")      
        
        irc_session.verify_disconnect(client1)

    
    def test_quit_after_registration4(self, irc_session):      
        """
        Connects two clients, and then has them quit, each with separate
        messages.
        """
        
        client1 = irc_session.connect_user("user1", "User One")
        client2 = irc_session.connect_user("user2", "User Two")
        
        client1.send_cmd("QUIT :See ya later!")
        client2.send_cmd("QUIT :Leaving")

        irc_session.get_message(client1, expect_cmd = "ERROR", expect_nparams = 1,
                                long_param_re = "Closing Link: .* \(See ya later!\)")      

        irc_session.get_message(client2, expect_cmd = "ERROR", expect_nparams = 1,
                                long_param_re = "Closing Link: .* \(Leaving\)")      
        
        irc_session.verify_disconnect(client1)
        irc_session.verify_disconnect(client2)
         
                       
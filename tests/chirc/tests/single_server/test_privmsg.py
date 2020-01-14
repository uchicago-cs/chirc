import re
import pytest

from chirc import replies

@pytest.mark.category("PRIVMSG_NOTICE")
class TestPRIVMSG(object):

    def test_privmsg1(self, irc_session):
        """
        Test sending a PRIVMSG from user1 to user2
        """        
        
        client1 = irc_session.connect_user("user1", "User One")
        client2 = irc_session.connect_user("user2", "User Two")
        
        client1.send_cmd("PRIVMSG user2 :Hello")
        
        irc_session.verify_relayed_privmsg(client2, from_nick="user1", recip="user2", msg="Hello")        


    def test_privmsg2(self, irc_session):
        """
        Test sending one hundred PRIVMSGs from user1 to user2
        """        

        client1 = irc_session.connect_user("user1", "User One")
        client2 = irc_session.connect_user("user2", "User Two")

        for i in range(100):
            client1.send_cmd("PRIVMSG user2 :Message %i" % (i+1))
            
        for i in range(100):
            irc_session.verify_relayed_privmsg(client2, from_nick="user1", recip="user2", msg="Message %i" % (i+1))


    def _test_multi_clients(self, irc_session, numclients, nummsgs, msg_timeout = None):
        """
        Connects `numclients` clients to the server, and then has them send
        `nummsgs` messages to each other.
        """
        
        clients = irc_session.connect_clients(numclients)
        
        if msg_timeout is not None:
            for nick, client in clients:
                client.msg_timeout = msg_timeout
        
        msgs_sent = set()
        msgs_rcvd = []
        
        for (nick1, client1) in clients:
            for (nick2, client2) in clients:
                if client1 != client2:
                    for i in range(nummsgs):
                        msg = "Message %i from %s to %s" % (i+1, nick1, nick2)
                        client1.send_cmd("PRIVMSG %s :%s" % (nick2, msg))
                        msgs_sent.add((nick1, nick2, msg))
                        
                        relayed_privmsg = irc_session.get_message(client2, expect_prefix = True, expect_cmd = "PRIVMSG", 
                                                                  expect_nparams = 2, expect_short_params = [nick2], 
                                                                  long_param_re = r"Message \d+ from user\d+ to user\d+")
                        msgs_rcvd.append( (relayed_privmsg.prefix.nick, nick2, relayed_privmsg) )

        pairs_seen = dict([((nick1, nick2),0) for (nick1,nick2,msg) in msgs_sent])
        for (from_nick, to_nick, msg) in msgs_rcvd:
            match = re.match(r":Message (?P<msgnum>\d+) from (?P<from>user\d+) to (?P<to>user\d+)", msg.params[-1])
            
            irc_session._assert_is_not_none(match, 
                                            "Received unexpected message (expected something of the form 'Message X from userN to userM')", 
                                            irc_msg = msg)
            
            from_nick2 = match.group("from")          
            to_nick2 = match.group("to")
            msgnum = int(match.group("msgnum"))
            
            irc_session._assert_equals(from_nick, from_nick2, 
                                       explanation = "The sender nick in the reply ({}) does not correspond to the one in the message".format(from_nick), 
                                       irc_msg = msg)            

            irc_session._assert_equals(to_nick, to_nick2, 
                                       explanation = "The recipient nick in the reply ({}) does not correspond to the one in the message".format(to_nick), 
                                       irc_msg = msg)            

            irc_session._assert_equals(pairs_seen[(from_nick, to_nick)], msgnum-1, 
                                       explanation = "Message arrived out of sequence (expected message {})".format(pairs_seen[(from_nick, to_nick)]+1), 
                                       irc_msg = msg)                      
                        
            pairs_seen[(from_nick, to_nick)] = msgnum
            
    def test_privmsg_multiple1(self, irc_session):
        """
        Test two users sending one message to each other.        
        """
        self._test_multi_clients(irc_session,2,1)

    def test_privmsg_multiple2(self, irc_session):
        """
        Test two users sending two messages to each other.        
        """
        self._test_multi_clients(irc_session,2,2)

    def test_privmsg_multiple3(self, irc_session):
        """
        Test four users sending two messages to each other.        
        """
        self._test_multi_clients(irc_session,4,2)

    def test_privmsg_multiple4(self, irc_session):
        """
        Test ten users sending two messages to each other.        
        """        
        self._test_multi_clients(irc_session,10,2, msg_timeout = 2.5)

    def test_privmsg_multiple5(self, irc_session):
        """
        Test twenty users sending five messages to each other.        
        """
        self._test_multi_clients(irc_session,20,5, msg_timeout = 5)

    def test_privmsg_nonick(self, irc_session):
        """
        Test sending a message to a user (user2) that does
        not exist in the server
        """
        
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("PRIVMSG user2 :Hello")

        irc_session.get_reply(client1, expect_code = replies.ERR_NOSUCHNICK, expect_nick = "user1", 
                              expect_nparams = 2, expect_short_params = ["user2"],
                              long_param_re = "No such nick/channel")     
        
    def test_privmsg_notext(self, irc_session):
        """
        Test sending a PRIVMSG without a message
        """
        
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("PRIVMSG user2")

        irc_session.get_reply(client1, expect_code = replies.ERR_NOTEXTTOSEND, expect_nick = "user1", 
                              expect_nparams = 1, long_param_re = "No text to send")     
              
    def test_privmsg_norecipient(self, irc_session):
        """
        Test sending a PRIVMSG without any parameters
        """
        
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("PRIVMSG")

        irc_session.get_reply(client1, expect_code = replies.ERR_NORECIPIENT, expect_nick = "user1", 
                              expect_nparams = 1, long_param_re = r"No recipient given \(PRIVMSG\)")
        

@pytest.mark.category("PRIVMSG_NOTICE")
class TestNOTICE(object):
    
    def test_notice(self, irc_session):
        """
        Test sending a NOTICE from user1 to user2
        """
        
        client1 = irc_session.connect_user("user1", "User One")
        client2 = irc_session.connect_user("user2", "User Two")
        
        client1.send_cmd("NOTICE user2 :Hello")
        
        irc_session.verify_relayed_notice(client2, from_nick="user1", recip="user2", msg="Hello")        
    
    def test_notice_nonick(self, irc_session):
        """
        Test sending a NOTICE to a user (user2) that doesn't exist in the server.
        """
        
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("NOTICE user2 :Hello")

        irc_session.get_reply(client1, expect_timeout = True)
        
    def test_notice_params1(self, irc_session):
        """
        Test sending a NOTICE with insufficient parameters.
        """
        
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("NOTICE user2")

        irc_session.get_reply(client1, expect_timeout = True)        
          
    def test_notice_params2(self, irc_session):
        """
        Test sending a NOTICE with insufficient parameters.
        """
        
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("NOTICE")

        irc_session.get_reply(client1, expect_timeout = True)        

    
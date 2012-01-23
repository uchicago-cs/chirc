import tests.replies as replies
import time
import re
from tests.common import ChircTestCase, ChircClient, ReplyTimeoutException
from tests.scores import score

class PRIVMSG(ChircTestCase):

    @score(category="PRIVMSG_NOTICE")
    def test_privmsg(self):
        client1 = self._connect_user("user1", "User One")
        client2 = self._connect_user("user2", "User Two")
        
        client1.send_cmd("PRIVMSG user2 :Hello")
        
        self._test_relayed_privmsg(client2, from_nick="user1", recip="user2", msg="Hello")        


    @score(category="PRIVMSG_NOTICE")
    def test_privmsg2(self):
        client1 = self._connect_user("user1", "User One")
        client2 = self._connect_user("user2", "User Two")

        for i in range(100):
            client1.send_cmd("PRIVMSG user2 :Message %i" % (i+1))
            
        for i in range(100):
            self._test_relayed_privmsg(client2, from_nick="user1", recip="user2", msg="Message %i" % (i+1))


    def _test_multi_clients(self, numclients, nummsgs, msg_timeout = None):
        clients = self._clients_connect(numclients)
        
        if msg_timeout is not None:
            for nick, client in clients:
                client.msg_timeout = msg_timeout
        
        msgs_sent = set()
        
        for (nick1, client1) in clients:
            for (nick2, client2) in clients:
                if client1 != client2:
                    for i in range(nummsgs):
                        msg = "Message %i from %s to %s" % (i+1, nick1, nick2)
                        client1.send_cmd("PRIVMSG %s :%s" % (nick2, msg))
                        msgs_sent.add((nick1, nick2, msg))

        msgs_rcvd = []
        for (nick1, client1) in clients:
            for i in range( (numclients - 1) * nummsgs):
                relayed_privmsg = self.get_message(client1, expect_prefix = True, expect_cmd = "PRIVMSG", 
                                                  expect_nparams = 2, expect_short_params = [nick1], 
                                                  long_param_re = "Message \d+ from user\d+ to user\d+")
                msgs_rcvd.append( (relayed_privmsg.prefix.nick, nick1, relayed_privmsg.params[-1]) )

        pairs_seen = dict([((nick1, nick2),0) for (nick1,nick2,msg) in msgs_sent])
        for (from_nick, to_nick, msg) in msgs_rcvd:
            match = re.match(":Message (?P<msgnum>\d+) from (?P<from>user\d+) to (?P<to>user\d+)", msg)
            self.assertIsNotNone(match)
            from_nick2 = match.group("from")          
            to_nick2 = match.group("to")
            msgnum = int(match.group("msgnum"))
            
            self.assertEqual(from_nick, from_nick2, "The sender nick in the reply (%s) does not correspond to the one in the message: %s" % (from_nick, msg))          
            self.assertEqual(to_nick, to_nick2, "The recipient nick in the reply (%s) does not correspond to the one in the message: %s" % (to_nick, msg))
            
            self.assertEqual(pairs_seen[(from_nick, to_nick)], msgnum-1, "Message arrived out of sequence (expected message %i)" % (pairs_seen[(from_nick, to_nick)]+1))
            
            pairs_seen[(from_nick, to_nick)] = msgnum
            
    @score(category="PRIVMSG_NOTICE")
    def test_privmsg_multiple1(self):
        self._test_multi_clients(2,1)

    @score(category="PRIVMSG_NOTICE")
    def test_privmsg_multiple2(self):
        self._test_multi_clients(2,2)

    @score(category="PRIVMSG_NOTICE")
    def test_privmsg_multiple3(self):
        self._test_multi_clients(4,2)

    @score(category="PRIVMSG_NOTICE")
    def test_privmsg_multiple4(self):
        self._test_multi_clients(10,2, msg_timeout = 2.5)

    @score(category="PRIVMSG_NOTICE")
    def test_privmsg_multiple5(self):
        self._test_multi_clients(20,5, msg_timeout = 5)

    @score(category="PRIVMSG_NOTICE")
    def test_privmsg_nonick(self):
        client1 = self._connect_user("user1", "User One")
        
        client1.send_cmd("PRIVMSG user2 :Hello")

        reply = self.get_reply(client1, expect_code = replies.ERR_NOSUCHNICK, expect_nick = "user1", 
                               expect_nparams = 2, expect_short_params = ["user2"],
                               long_param_re = "No such nick/channel")           
        

class NOTICE(ChircTestCase):
    
    @score(category="PRIVMSG_NOTICE")
    def test_notice(self):
        client1 = self._connect_user("user1", "User One")
        client2 = self._connect_user("user2", "User Two")
        
        client1.send_cmd("NOTICE user2 :Hello")
        
        self._test_relayed_notice(client2, from_nick="user1", recip="user2", msg="Hello")        
    
    @score(category="PRIVMSG_NOTICE")
    def test_notice_nonick(self):
        client1 = self._connect_user("user1", "User One")
        
        client1.send_cmd("NOTICE user2 :Hello")

        self.assertRaises(ReplyTimeoutException, self.get_reply, client1)        
    
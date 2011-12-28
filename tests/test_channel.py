import tests.replies as replies
import time
import re
from tests.common import ChircTestCase, ChircClient, ReplyTimeoutException
from tests.scores import score

class JOIN(ChircTestCase):

    @score(category="CHANNEL_JOIN")
    def test_join1(self):
        client1 = self._connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        
        self._test_join(client1, "user1", "#test")
        
    @score(category="CHANNEL_JOIN")
    def test_join2(self):
        client1 = self._connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        
        self._test_join(client1, "user1", "#test")

        client1.send_cmd("JOIN #test")
        self.assertRaises(ReplyTimeoutException, self.get_reply, client1) 
        
    @score(category="CHANNEL_JOIN")
    def test_join3(self):
        clients = self._clients_connect(5)

        for (nick, client) in clients:
            client.send_cmd("JOIN #test")
            self._test_join(client, nick, "#test")        
        
    @score(category="CHANNEL_JOIN")
    def test_join4(self):
        client1 = self._connect_user("user1", "User One")
        client2 = self._connect_user("user2", "User Two")
        
        client1.send_cmd("JOIN #test")
        
        self._test_join(client1, "user1", "#test")

        client2.send_cmd("JOIN #test")
        self._test_join(client2, "user2", "#test")
        
        self._test_relayed_join(client1, from_nick="user2", channel="#test")
        
    @score(category="CHANNEL_JOIN")
    def test_join5(self):
        clients = self._clients_connect(5)

        for (nick, client) in clients:
            client.send_cmd("JOIN #test")
            self._test_join(client, nick, "#test")  
            
        relayed = len(clients) - 1
        for (nick, client) in clients:
            for i in range(relayed):
                self._test_relayed_join(client, from_nick = None, channel="#test")
            relayed -= 1
        

class PRIVMSG(ChircTestCase):
    
    def _test_join_and_privmsg(self, numclients):
        clients = self._clients_connect(numclients, join_channel = "#test")
        
        for (nick1, client1) in clients:
            client1.send_cmd("PRIVMSG #test :Hello from %s!" % nick1)
            for (nick2, client2) in clients:
                if nick1 != nick2:
                    self._test_relayed_privmsg(client2, from_nick=nick1, recip="#test", msg="Hello from %s!" % nick1)  
    
    @score(category="CHANNEL_PRIVMSG_NOTICE")
    def test_channel_privmsg1(self):
        self._test_join_and_privmsg(2)
        
    @score(category="CHANNEL_PRIVMSG_NOTICE")
    def test_channel_privmsg2(self):
        self._test_join_and_privmsg(5)

    @score(category="CHANNEL_PRIVMSG_NOTICE")
    def test_channel_privmsg3(self):
        self._test_join_and_privmsg(20)
        
    @score(category="CHANNEL_PRIVMSG_NOTICE")
    def test_channel_privmsg_nochannel(self):
        client1 = self._connect_user("user1", "User One")
        
        client1.send_cmd("PRIVMSG #test :Hello")

        reply = self.get_reply(client1, expect_code = replies.ERR_NOSUCHNICK, expect_nick = "user1", 
                               expect_nparams = 2, expect_short_params = ["#test"],
                               long_param_re = "No such nick/channel")      
        
class NOTICE(ChircTestCase):     
    
    @score(category="CHANNEL_PRIVMSG_NOTICE")
    def test_channel_notice_nochannel(self):
        client1 = self._connect_user("user1", "User One")
        
        client1.send_cmd("NOTICE #test :Hello")

        self.assertRaises(ReplyTimeoutException, self.get_reply, client1)   
        
class PART(ChircTestCase):
    def _test_join_and_part(self, numclients):
        clients = self._clients_connect(numclients, join_channel = "#test")
        self._clients_part(clients, "#test")
        
    def _test_join_and_part_and_join_and_part(self, numclients):
        clients = self._clients_connect(numclients, join_channel = "#test")
        self._clients_part(clients, "#test")        
        self._clients_join(clients, "#test")
        self._clients_part(clients, "#test")

    @score(category="CHANNEL_PART")
    def test_channel_part1(self):
        clients = self._clients_connect(2, join_channel = "#test")
        
        nick1, client1 = clients[0]
        nick2, client2 = clients[1]
        
        client1.send_cmd("PART #test")
        self._test_relayed_part(client1, from_nick=nick1, channel="#test", msg=None)
        self._test_relayed_part(client2, from_nick=nick1, channel="#test", msg=None)

    @score(category="CHANNEL_PART")
    def test_channel_part2(self):
        clients = self._clients_connect(2, join_channel = "#test")
        
        nick1, client1 = clients[0]
        nick2, client2 = clients[1]
        
        client1.send_cmd("PART #test :I'm out of here!")
        self._test_relayed_part(client1, from_nick=nick1, channel="#test", msg="I'm out of here!")
        self._test_relayed_part(client2, from_nick=nick1, channel="#test", msg="I'm out of here!")
                
    @score(category="CHANNEL_PART")
    def test_channel_part3(self):
        clients = self._clients_connect(2, join_channel = "#test")
        
        nick1, client1 = clients[0]
        nick2, client2 = clients[1]
        
        client1.send_cmd("PRIVMSG #test :Hello!")
        self._test_relayed_privmsg(client2, from_nick=nick1, recip="#test", msg="Hello!")
        
        client2.send_cmd("PART #test")
        self._test_relayed_part(client2, from_nick=nick2, channel="#test", msg=None)          
        self._test_relayed_part(client1, from_nick=nick2, channel="#test", msg=None)
        
        client1.send_cmd("PRIVMSG #test :Hello?")
        self.assertRaises(ReplyTimeoutException, self.get_reply, client2)
                
    @score(category="CHANNEL_PART")
    def test_channel_part4(self):
        self._test_join_and_part(2)
        
    @score(category="CHANNEL_PART")
    def test_channel_part5(self):
        self._test_join_and_part(5)

    @score(category="CHANNEL_PART")
    def test_channel_part6(self):
        self._test_join_and_part(20)         
        
    @score(category="CHANNEL_PART")
    def test_channel_part7(self):
        self._test_join_and_part_and_join_and_part(2)

    @score(category="CHANNEL_PART")
    def test_channel_part8(self):
        self._test_join_and_part_and_join_and_part(5)

    @score(category="CHANNEL_PART")
    def test_channel_part9(self):
        self._test_join_and_part_and_join_and_part(10)

    @score(category="CHANNEL_PART")
    def test_channel_part_nochannel1(self):
        client1 = self._connect_user("user1", "User One")
        
        client1.send_cmd("PART #test")

        reply = self.get_reply(client1, expect_code = replies.ERR_NOSUCHCHANNEL, expect_nick = "user1", 
                               expect_nparams = 2, expect_short_params = ["#test"],
                               long_param_re = "No such channel")      
        
    @score(category="CHANNEL_PART")
    def test_channel_part_nochannel2(self):
        clients = self._clients_connect(1, join_channel = "#test")
        self._clients_part(clients, "#test")  
        
        nick1, client1 = clients[0]
      
        client1.send_cmd("PART #test")

        reply = self.get_reply(client1, expect_code = replies.ERR_NOSUCHCHANNEL, expect_nick = nick1, 
                               expect_nparams = 2, expect_short_params = ["#test"],
                               long_param_re = "No such channel")              
        
    @score(category="CHANNEL_PART")
    def test_channel_part_notonchannel1(self):
        client1 = self._connect_user("user1", "User One")
        client2 = self._connect_user("user2", "User Two")
        
        client1.send_cmd("JOIN #test")   
        self._test_join(client1, "user1", "#test")
          
        client2.send_cmd("PART #test")
            
        reply = self.get_reply(client2, expect_code = replies.ERR_NOTONCHANNEL, expect_nick = "user2", 
                               expect_nparams = 2, expect_short_params = ["#test"],
                               long_param_re = "You're not on that channel")          
        
    @score(category="CHANNEL_PART")
    def test_channel_part_notonchannel2(self):
        clients = self._clients_connect(2, join_channel = "#test") 
        
        nick1, client1 = clients[0]
        client1.send_cmd("PART #test")
        self._test_relayed_part(client1, from_nick=nick1, channel="#test", msg=None)    

        client1.send_cmd("PART #test")
        reply = self.get_reply(client1, expect_code = replies.ERR_NOTONCHANNEL, expect_nick = nick1, 
                               expect_nparams = 2, expect_short_params = ["#test"],
                               long_param_re = "You're not on that channel")                
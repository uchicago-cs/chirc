import tests.replies as replies
import time
import re
from tests.common import ChircTestCase, ChircClient, ReplyTimeoutException, OPER_PASSWD
from tests.common import channels1, channels2, channels3, channels4
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
        
    @score(category="CHANNEL_PRIVMSG_NOTICE")
    def test_channel_privmsg_notonchannel(self):
        client1 = self._connect_user("user1", "User One")

        client1.send_cmd("JOIN #test")
        self._test_join(client1, "user1", "#test")  

        client2 = self._connect_user("user2", "User Two")  
        client2.send_cmd("PRIVMSG #test :Hello")      
        
        self.get_reply(client2, expect_code = replies.ERR_CANNOTSENDTOCHAN, expect_nick = "user2", 
                       expect_nparams = 2, expect_short_params = ["#test"],
                       long_param_re = "Cannot send to channel")          
          
        
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
        
        
class TOPIC(ChircTestCase):
    @score(category="CHANNEL_TOPIC")
    def test_topic1(self):
        topic = "This is the channel's topic"
        
        client1 = self._connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        
        self._test_join(client1, "user1", "#test")    
        
        client1.send_cmd("TOPIC #test :%s" % topic)
        
        self._test_relayed_topic(client1, from_nick="user1", channel="#test", topic=topic)

    @score(category="CHANNEL_TOPIC")
    def test_topic2(self):
        topic = "This is the channel's topic"
        
        client1 = self._connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        
        self._test_join(client1, "user1", "#test")    
        
        client1.send_cmd("TOPIC #test :%s" % topic)
        
        self._test_relayed_topic(client1, from_nick="user1", channel="#test", topic=topic)
        
        client1.send_cmd("TOPIC #test")
        
        reply = self.get_reply(client1, expect_code = replies.RPL_TOPIC, expect_nick = "user1", 
                               expect_nparams = 2, expect_short_params = ["#test"],
                               long_param_re = topic)        

    @score(category="CHANNEL_TOPIC")
    def test_topic3(self):
        client1 = self._connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        
        self._test_join(client1, "user1", "#test")    
        
        client1.send_cmd("TOPIC #test")
        
        reply = self.get_reply(client1, expect_code = replies.RPL_NOTOPIC, expect_nick = "user1", 
                               expect_nparams = 2, expect_short_params = ["#test"],
                               long_param_re = "No topic is set")        
        
    @score(category="CHANNEL_TOPIC")
    def test_topic4(self):
        client1 = self._connect_user("user1", "User One")
        
        client1.send_cmd("TOPIC #test")
        
        reply = self.get_reply(client1, expect_code = replies.ERR_NOTONCHANNEL, expect_nick = "user1", 
                               expect_nparams = 2, expect_short_params = ["#test"],
                               long_param_re = "You're not on that channel")             
    
    @score(category="CHANNEL_TOPIC")
    def test_topic4(self):
        client1 = self._connect_user("user1", "User One")
        
        client1.send_cmd("TOPIC #test :This is the channel's topic")
        
        reply = self.get_reply(client1, expect_code = replies.ERR_NOTONCHANNEL, expect_nick = "user1", 
                               expect_nparams = 2, expect_short_params = ["#test"],
                               long_param_re = "You're not on that channel")       
        
    @score(category="CHANNEL_TOPIC")
    def test_topic5(self):
        client1 = self._connect_user("user1", "User One")
        client2 = self._connect_user("user2", "User Two")
        
        client1.send_cmd("JOIN #test")
        self._test_join(client1, "user1", "#test")    
        
        client2.send_cmd("TOPIC #test")
        reply = self.get_reply(client2, expect_code = replies.ERR_NOTONCHANNEL, expect_nick = "user2", 
                               expect_nparams = 2, expect_short_params = ["#test"],
                               long_param_re = "You're not on that channel")       

    @score(category="CHANNEL_TOPIC")
    def test_topic6(self):
        client1 = self._connect_user("user1", "User One")
        client2 = self._connect_user("user2", "User Two")
       
        topic = "This is the channel's topic"
        client1.send_cmd("JOIN #test")
        self._test_join(client1, "user1", "#test")    
        client1.send_cmd("TOPIC #test :%s" % topic)
        self._test_relayed_topic(client1, from_nick="user1", channel="#test", topic=topic)
        
        client2.send_cmd("TOPIC #test")
        reply = self.get_reply(client2, expect_code = replies.ERR_NOTONCHANNEL, expect_nick = "user2", 
                               expect_nparams = 2, expect_short_params = ["#test"],
                               long_param_re = "You're not on that channel")       
  
    @score(category="CHANNEL_TOPIC")
    def test_topic7(self):
        client1 = self._connect_user("user1", "User One")
        client2 = self._connect_user("user2", "User Two")
       
        topic = "This is the channel's topic"
        client1.send_cmd("JOIN #test")
        self._test_join(client1, "user1", "#test")    
        client1.send_cmd("TOPIC #test :%s" % topic)
        self._test_relayed_topic(client1, from_nick="user1", channel="#test", topic=topic)

        client2.send_cmd("JOIN #test")
        self._test_join(client2, "user2", "#test", expect_topic=topic)    
        
    @score(category="CHANNEL_TOPIC")
    def test_topic8(self):
        clients = self._clients_connect(10, join_channel = "#test")
        
        nick1, client1 = clients[0]
        
        topic = "This is the channel's topic"
        client1.send_cmd("TOPIC #test :%s" % topic)
                
        for nick, client in clients:
            self._test_relayed_topic(client, from_nick=nick1, channel="#test", topic=topic)    
            
    @score(category="CHANNEL_TOPIC")
    def test_topic9(self):
        clients = self._clients_connect(10)
        
        nick1, client1 = clients[0]
        
        topic = "This is the channel's topic"
        client1.send_cmd("JOIN #test")
        self._test_join(client1, "user1", "#test")    
        client1.send_cmd("TOPIC #test :%s" % topic)
        self._test_relayed_topic(client1, from_nick="user1", channel="#test", topic=topic)
        
        for nick, client in clients[1:]:
            client.send_cmd("JOIN #test")
            self._test_join(client, nick, "#test", expect_topic=topic)    
        
        
class NAMES(ChircTestCase):
    
    def _test_names_channel(self, channels, client, nick):
        channelsl = [k for k in channels.keys() if k is not None]
        channelsl.sort()
        for channel in channelsl:
            channelusers = channels[channel]
            client.send_cmd("NAMES %s" % channel)
            self._test_names(client, nick, expect_channel = channel, expect_names = channelusers)
            
    def _test_names_all(self, channels, client, nick):
        client.send_cmd("NAMES")

        channelsl = set([k for k in channels.keys() if k is not None])
        numchannels = len(channelsl)
        
        for i in range(numchannels):
            reply = self.get_reply(client, expect_code = replies.RPL_NAMREPLY, expect_nick = nick,
                           expect_nparams = 3)    
            channel = reply.params[2]
            self.assertIn(channel, channelsl, "Received unexpected RPL_NAMREPLY for %s: %s" % (channel, reply._s))    
            self._test_names_single(reply, nick, expect_channel = channel, expect_names = channels[channel])
            channelsl.remove(channel)
            
        self.assertEqual(len(channelsl), 0, "Did not receive RPL_NAMREPLY for these channels: %s" % (", ".join(channelsl)))
                
        if not channels.has_key(None):
            no_channel = []
        else:
            no_channel = channels[None]
            
        if len(no_channel) > 0:
            self._test_names(client, nick, expect_channel = "*", expect_names = no_channel)
        else:
            self.get_reply(client, expect_code = replies.RPL_ENDOFNAMES, expect_nick = nick,
                       expect_nparams = 2)    
     

    @score(category="NAMES")
    def test_names1(self):
        self._channels_connect(channels1, test_names = True)
        
    @score(category="NAMES")
    def test_names2(self):
        self._channels_connect(channels2, test_names = True)

    @score(category="NAMES")
    def test_names3(self):
        self._channels_connect(channels3, test_names = True)     
        

    @score(category="NAMES")
    def test_names4(self):
        users = self._channels_connect(channels1, test_names = True)
        
        self._test_names_channel(channels1, users["user1"], "user1")
        
    @score(category="NAMES")
    def test_names5(self):
        users = self._channels_connect(channels2, test_names = True)
        
        self._test_names_channel(channels2, users["user1"], "user1")

    @score(category="NAMES")
    def test_names6(self):
        users = self._channels_connect(channels3, test_names = True)
        
        self._test_names_channel(channels3, users["user1"], "user1")
        
        
    @score(category="NAMES")
    def test_names7(self):
        users = self._channels_connect(channels1, test_names = True)
        
        self._test_names_all(channels1, users["user1"], "user1")
        
    @score(category="NAMES")
    def test_names8(self):
        users = self._channels_connect(channels2, test_names = True)
        
        self._test_names_all(channels2, users["user1"], "user1")

    @score(category="NAMES")
    def test_names9(self):
        users = self._channels_connect(channels3, test_names = True)                    
        
        self._test_names_all(channels3, users["user1"], "user1")
        
    @score(category="NAMES")
    def test_names10(self):
        users = self._channels_connect(channels4, test_names = True)                    
        
        self._test_names_all(channels4, users["user1"], "user1")        
        
        
    @score(category="NAMES")
    def test_names11(self):
        users = self._channels_connect(channels1, test_names = True)
        
        users["user1"].send_cmd("NAMES #noexist")
        self.get_reply(users["user1"], expect_code = replies.RPL_ENDOFNAMES, expect_nick = "user1",
                   expect_nparams = 2)                


class LIST(ChircTestCase):
            
    def _test_list(self, channels, client, nick, expect_topics = None):
        client.send_cmd("LIST")

        channelsl = set([k for k in channels.keys() if k is not None])
        numchannels = len(channelsl)
        
        for i in range(numchannels):
            reply = self.get_reply(client, expect_code = replies.RPL_LIST, expect_nick = nick,
                           expect_nparams = 3)    

            channel = reply.params[1]
            self.assertIn(channel, channelsl, "Received unexpected RPL_LIST for %s: %s" % (channel, reply._s))    

            numusers = int(reply.params[2])
            expect_numusers = len(channels[channel])
            self.assertEqual(numusers, expect_numusers, "Expected %i users in %s, got %i: %s" % (expect_numusers, channel, numusers, reply._s))    
            
            if expect_topics is not None:
                expect_topic = expect_topics[channel]
                topic = reply.params[3][1:]
                self.assertEqual(topic, expect_topic, "Expected topic for %s to be '%s', got '%s' instead: %s" % (channel, expect_topic, topic, reply._s))    
                
            channelsl.remove(channel)
            
        self.assertEqual(len(channelsl), 0, "Did not receive RPL_LIST for these channels: %s" % (", ".join(channelsl)))
                
        self.get_reply(client, expect_code = replies.RPL_LISTEND, expect_nick = nick,
                       expect_nparams = 1, long_param_re = "End of LIST")    
        

    @score(category="LIST")
    def test_list1(self):
        users = self._channels_connect(channels1)
        
        self._test_list(channels1, users["user1"], "user1")
        
    @score(category="LIST")
    def test_list2(self):
        users = self._channels_connect(channels2)
        
        self._test_list(channels2, users["user1"], "user1")
        
    @score(category="LIST")
    def test_list3(self):
        users = self._channels_connect(channels3)
        
        self._test_list(channels3, users["user1"], "user1")
        
    @score(category="LIST")
    def test_list4(self):
        users = self._channels_connect(channels4)
        
        self._test_list(channels4, users["user1"], "user1")        
        
  
    @score(category="LIST")
    def test_list5(self):
        users = self._channels_connect(channels2)
        
        users["user1"].send_cmd("TOPIC #test1 :Topic One")
        self._test_relayed_topic(users["user1"], from_nick="user1", channel="#test1", topic="Topic One")
        
        users["user4"].send_cmd("TOPIC #test2 :Topic Two")
        self._test_relayed_topic(users["user4"], from_nick="user4", channel="#test2", topic="Topic Two")

        users["user7"].send_cmd("TOPIC #test3 :Topic Three")
        self._test_relayed_topic(users["user7"], from_nick="user7", channel="#test3", topic="Topic Three")

        self._test_list(channels2, users["user10"], "user10",
                        expect_topics = {"#test1": "Topic One",
                                         "#test2": "Topic Two",
                                         "#test3": "Topic Three"})      
        
        
class WHO(ChircTestCase):
            
    def _test_who(self, channels, client, nick, channel, aways = None, ircops = None):
        client.send_cmd("WHO %s" % channel)

        if channel == "*":
            users = set()
            for chan, channelusers in channels.items():
                channelusers2 = set()
                for user in channelusers:
                    if user[0] in ("@", "+"):
                        nick2 = user[1:]
                    else:
                        nick2 = user
                    channelusers2.add(nick2)
                if chan is None or nick not in channelusers2:
                    users.update(channelusers2)
            numusers = len(users)
        else:    
            users = set(channels[channel])
            numusers = len(users)

        for i in range(numusers):
            reply = self.get_reply(client, expect_code = replies.RPL_WHOREPLY, expect_nick = nick,
                           expect_nparams = 7, expect_short_params = [channel])
            
            ircop = False
            away = False
            who_nick = reply.params[5]
            status = reply.params[6]
            
            self.assertIn(len(status), (1,2,3), "Invalid status string '%s': %s" % (status, reply._s))    
            
            self.assertIn(status[0], ('H','G'), "Invalid status string '%s': %s" % (status, reply._s))
            
            if status[0] == 'G':
                away = True

            if len(status) == 1:
                qwho_nick = who_nick
            if len(status) == 2:
                if status[1] == '*':
                    ircop = True
                    qwho_nick = who_nick
                else:
                    self.assertIn(status[1], ('@','+'), "Invalid status string '%s': %s" % (status, reply._s))
                    qwho_nick = status[1] + who_nick
            elif len(status) == 3:
                self.assertEqual(status[1], '*', "Invalid status string '%s': %s" % (status, reply._s))
                self.assertIn(status[2], ('@','+'), "Invalid status string '%s': %s" % (status, reply._s))
                ircop = True
                qwho_nick = status[2] + who_nick
            
            self.assertIn(qwho_nick, users, "Received unexpected RPL_WHOREPLY for %s: %s" % (who_nick, reply._s))    

            if ircops is not None:
                if who_nick in ircops:
                    self.assertTrue(ircop, "Expected %s to be an IRCop: %s" % (who_nick, reply._s))
                else:    
                    self.assertFalse(ircop, "Did not expect %s to be an IRCop: %s" % (who_nick, reply._s))
            
            if aways is not None:
                if who_nick in aways:
                    self.assertTrue(away, "Expected %s to be away: %s" % (who_nick, reply._s))
                else:    
                    self.assertFalse(away, "Did not expect %s to be away: %s" % (who_nick, reply._s))
                
            users.remove(qwho_nick)
            
        self.assertEqual(len(users), 0, "Did not receive RPL_WHOREPLY for these users: %s" % (", ".join(users)))
                
        self.get_reply(client, expect_code = replies.RPL_ENDOFWHO, expect_nick = nick,
                       expect_nparams = 2, expect_short_params = [channel],
                       long_param_re = "End of WHO list")    
        

    @score(category="WHO")
    def test_who1(self):
        users = self._channels_connect(channels1)
        
        self._test_who(channels1, users["user1"], "user1", channel = "#test1")        
        self._test_who(channels1, users["user1"], "user1", channel = "#test2")        
        self._test_who(channels1, users["user1"], "user1", channel = "#test3")
        
    @score(category="WHO")
    def test_who2(self):
        users = self._channels_connect(channels1)
        
        self._test_who(channels1, users["user1"], "user1", channel = "*")        
        self._test_who(channels1, users["user4"], "user4", channel = "*")        
        self._test_who(channels1, users["user7"], "user7", channel = "*")        
        
    @score(category="WHO")
    def test_who3(self):
        users = self._channels_connect(channels2)
        
        self._test_who(channels2, users["user1"], "user1", channel = "*")        
        self._test_who(channels2, users["user4"], "user4", channel = "*")        
        self._test_who(channels2, users["user7"], "user7", channel = "*")             
        self._test_who(channels2, users["user10"], "user10", channel = "*")             
        
    @score(category="WHO")
    def test_who4(self):
        users = self._channels_connect(channels3)
        
        self._test_who(channels3, users["user1"], "user1", channel = "#test1")        
        self._test_who(channels3, users["user1"], "user1", channel = "#test2")        
        self._test_who(channels3, users["user1"], "user1", channel = "#test3")                     
        self._test_who(channels3, users["user1"], "user1", channel = "#test4")        
        self._test_who(channels3, users["user1"], "user1", channel = "#test5")       
        
        
    @score(category="WHO")
    def test_who5(self):
        aways = ["user4", "user5", "user7"]
        ircops = ["user4", "user6"]

        users = self._channels_connect(channels1, aways, ircops)
                
        self._test_who(channels1, users["user1"], "user1", channel = "#test1", aways = aways, ircops = ircops)        
        self._test_who(channels1, users["user1"], "user1", channel = "#test2", aways = aways, ircops = ircops)        
        self._test_who(channels1, users["user1"], "user1", channel = "#test3", aways = aways, ircops = ircops)     
        
        
    @score(category="WHO")
    def test_who6(self):
        aways = ["user4", "user8", "user10"]
        ircops = ["user8", "user9", "user10", "user11"]
        
        users = self._channels_connect(channels3, aways, ircops)     
        
        self._test_who(channels3, users["user1"], "user1", channel = "#test1", aways = aways, ircops = ircops)        
        self._test_who(channels3, users["user1"], "user1", channel = "#test2", aways = aways, ircops = ircops)        
        self._test_who(channels3, users["user1"], "user1", channel = "#test3", aways = aways, ircops = ircops)                     
        self._test_who(channels3, users["user1"], "user1", channel = "#test4", aways = aways, ircops = ircops)        
        self._test_who(channels3, users["user1"], "user1", channel = "#test5", aways = aways, ircops = ircops)                            
                 
                 
class UPDATE1b(ChircTestCase):
                                    
    @score(category="UPDATE_1B")
    def test_update1b_nick(self):
        clients = self._clients_connect(5, join_channel = "#test")
        
        nick1, client1 = clients[0]
        
        client1.send_cmd("NICK userfoo")
                
        for nick, client in clients:
            self._test_relayed_nick(client, from_nick=nick1, newnick="userfoo")         
            
    @score(category="UPDATE_1B")
    def test_update1b_quit1(self):
        clients = self._clients_connect(5, join_channel = "#test")
        
        nick1, client1 = clients[0]
        
        client1.send_cmd("QUIT")
                
        for nick, client in clients[1:]:
            self._test_relayed_quit(client, from_nick=nick1, msg = None)           
            
    @score(category="UPDATE_1B")
    def test_update1b_quit2(self):
        clients = self._clients_connect(5, join_channel = "#test")
        
        nick1, client1 = clients[0]
        
        client1.send_cmd("QUIT :I'm outta here")
                
        for nick, client in clients[1:]:
            self._test_relayed_quit(client, from_nick=nick1, msg = "I'm outta here")                                                    
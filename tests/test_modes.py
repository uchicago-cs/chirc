import tests.replies as replies
import time
import re
from tests.common import ChircTestCase, ChircClient, ReplyTimeoutException, OPER_PASSWD
from tests.common import channels1, channels2, channels3, channels4
from tests.scores import score

class OPER(ChircTestCase):

    @score(category="MODES")
    def test_oper1(self):
        client1 = self._connect_user("user1", "User One")
        
        client1.send_cmd("OPER user1 %s" % OPER_PASSWD)
        
        reply = self.get_reply(client1, expect_code = replies.RPL_YOUREOPER, expect_nick = "user1", 
                               expect_nparams = 1,
                               long_param_re = "You are now an IRC operator")      
        
    @score(category="MODES")
    def test_oper2(self):
        client1 = self._connect_user("user1", "User One")
        
        client1.send_cmd("OPER user1 BAD%s" % OPER_PASSWD)
        
        reply = self.get_reply(client1, expect_code = replies.ERR_PASSWDMISMATCH, expect_nick = "user1", 
                               expect_nparams = 1,
                               long_param_re = "Password incorrect")
        
class MODE(ChircTestCase):       
     
    @score(category="MODES")
    def test_user_mode1(self):
        client1 = self._connect_user("user1", "User One")
        
        self._user_mode(client1, "user1", "user1", "+o", expect_relay=False)
    
    @score(category="MODES")
    def test_user_mode2(self):
        client1 = self._connect_user("user1", "User One")
        
        self._user_mode(client1, "user1", "user1", "-o")

    @score(category="MODES")
    def test_user_mode3(self):
        client1 = self._connect_user("user1", "User One")
        
        self._user_mode(client1, "user1", "user1", "+a", expect_relay=False)

    @score(category="MODES")
    def test_user_mode4(self):
        client1 = self._connect_user("user1", "User One")
        
        self._user_mode(client1, "user1", "user1", "-a", expect_relay=False)
        
    @score(category="MODES")
    def test_user_mode5(self):
        client1 = self._connect_user("user1", "User One")
        
        self._user_mode(client1, "user1", "user1", "+v", expect_wrong_mode=True)
        
    @score(category="MODES")
    def test_user_mode6(self):
        client1 = self._connect_user("user1", "User One")
        
        self._user_mode(client1, "user1", "user1", "-v", expect_wrong_mode=True)
        
    @score(category="MODES")
    def test_user_mode7(self):
        client1 = self._connect_user("user1", "User One")
        
        self._user_mode(client1, "user1", "user1", "+t", expect_wrong_mode=True)
        
    @score(category="MODES")
    def test_user_mode8(self):
        client1 = self._connect_user("user1", "User One")
        
        self._user_mode(client1, "user1", "user1", "-t", expect_wrong_mode=True)        
        
    @score(category="MODES")
    def test_user_mode9(self):
        client1 = self._connect_user("user1", "User One")
        
        self._user_mode(client1, "user1", "user1", "+z", expect_wrong_mode=True)
        
    @score(category="MODES")
    def test_user_mode10(self):
        client1 = self._connect_user("user1", "User One")
        
        self._user_mode(client1, "user1", "user1", "-z", expect_wrong_mode=True)        
        
    @score(category="MODES")
    def test_user_mode11(self):
        client1 = self._connect_user("user1", "User One")
        
        self._user_mode(client1, "user1", "user2", "-o")   

    @score(category="MODES")
    def test_user_mode12(self):
        client1 = self._connect_user("user1", "User One")
        
        self._user_mode(client1, "user1", "user2", "-z")   
        

    @score(category="MODES")
    def test_channel_mode1(self):
        client1 = self._connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        self._test_join(client1, "user1", "#test")
        
        self._channel_mode(client1, "user1", "#test", "+m")
        self._test_relayed_mode(client1, "user1", "#test", "+m")
        
    @score(category="MODES")
    def test_channel_mode2(self):
        client1 = self._connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        self._test_join(client1, "user1", "#test")
        
        self._channel_mode(client1, "user1", "#test", "+t")
        self._test_relayed_mode(client1, "user1", "#test", "+t")        
        
    @score(category="MODES")
    def test_channel_mode3(self):
        client1 = self._connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        self._test_join(client1, "user1", "#test")
        
        self._channel_mode(client1, "user1", "#test", "-m")
        self._test_relayed_mode(client1, "user1", "#test", "-m")
        
    @score(category="MODES")
    def test_channel_mode4(self):
        client1 = self._connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        self._test_join(client1, "user1", "#test")
        
        self._channel_mode(client1, "user1", "#test", "-t")
        self._test_relayed_mode(client1, "user1", "#test", "-t")
        
    @score(category="MODES")
    def test_channel_mode5(self):
        client1 = self._connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        self._test_join(client1, "user1", "#test")
        
        self._channel_mode(client1, "user1", "#test", "+z", expect_wrong_mode=True)               
        
    @score(category="MODES")
    def test_channel_mode6(self):
        client1 = self._connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        self._test_join(client1, "user1", "#test")
        
        self._channel_mode(client1, "user1", "#test", "+o", expect_wrong_mode=True)             
        
    @score(category="MODES")
    def test_channel_mode7(self):
        client1 = self._connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        self._test_join(client1, "user1", "#test")
        
        self._channel_mode(client1, "user1", "#test", "+v", expect_wrong_mode=True)        
        
    @score(category="MODES")
    def test_channel_mode8(self):
        client1 = self._connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        self._test_join(client1, "user1", "#test")
        
        self._channel_mode(client1, "user1", "#test", "+m")
        self._test_relayed_mode(client1, "user1", "#test", "+m")      
        
        self._channel_mode(client1, "user1", "#test", expect_mode = "m")
        
    @score(category="MODES")
    def test_channel_mode9(self):
        client1 = self._connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        self._test_join(client1, "user1", "#test")
        
        self._channel_mode(client1, "user1", "#test", "+m")
        self._test_relayed_mode(client1, "user1", "#test", "+m")      

        self._channel_mode(client1, "user1", "#test", "+t")
        self._test_relayed_mode(client1, "user1", "#test", "+t")      
        
        self._channel_mode(client1, "user1", "#test", expect_mode = "mt")           
        
    @score(category="MODES")
    def test_channel_mode10(self):
        client1 = self._connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        self._test_join(client1, "user1", "#test")
        
        self._channel_mode(client1, "user1", "#test", "+m")
        self._test_relayed_mode(client1, "user1", "#test", "+m")      

        self._channel_mode(client1, "user1", "#test", "+t")
        self._test_relayed_mode(client1, "user1", "#test", "+t")      

        self._channel_mode(client1, "user1", "#test", "-t")
        self._test_relayed_mode(client1, "user1", "#test", "-t")      
        
        self._channel_mode(client1, "user1", "#test", expect_mode = "m")                 
    
    @score(category="MODES")
    def test_channel_mode11(self):
        client1 = self._connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        self._test_join(client1, "user1", "#test")
        
        self._channel_mode(client1, "user1", "#test", "+m")
        self._test_relayed_mode(client1, "user1", "#test", "+m")      

        self._channel_mode(client1, "user1", "#test", "+t")
        self._test_relayed_mode(client1, "user1", "#test", "+t")      

        self._channel_mode(client1, "user1", "#test", "-m")
        self._test_relayed_mode(client1, "user1", "#test", "-m")      
        
        self._channel_mode(client1, "user1", "#test", expect_mode = "t")    
        
    @score(category="MODES")
    def test_channel_mode12(self):
        client1 = self._connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        self._test_join(client1, "user1", "#test")
        
        self._channel_mode(client1, "user1", "#test", "+m")
        self._test_relayed_mode(client1, "user1", "#test", "+m")      

        self._channel_mode(client1, "user1", "#test", "+t")
        self._test_relayed_mode(client1, "user1", "#test", "+t")      

        self._channel_mode(client1, "user1", "#test", "-m")
        self._test_relayed_mode(client1, "user1", "#test", "-m")      

        self._channel_mode(client1, "user1", "#test", "-t")
        self._test_relayed_mode(client1, "user1", "#test", "-t")      
        
        self._channel_mode(client1, "user1", "#test", expect_mode = "")         
        
    @score(category="MODES")
    def test_channel_mode13(self):
        client1 = self._connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        self._test_join(client1, "user1", "#test")  
        
        self._channel_mode(client1, "user1", "#test", expect_mode = "")       
        
    @score(category="MODES")
    def test_channel_mode14(self):
        client1 = self._connect_user("user1", "User One")
        
        self._channel_mode(client1, "user1", "#test", expect_wrong_channel = True)      
        
    @score(category="MODES")
    def test_channel_mode15(self):
        client1 = self._connect_user("user1", "User One")
        
        self._channel_mode(client1, "user1", "#test", "+m", expect_wrong_channel = True)      
        
    @score(category="MODES")
    def test_channel_mode16(self):
        client1 = self._connect_user("user1", "User One")
        
        self._channel_mode(client1, "user1", "#test", "+o", expect_wrong_channel = True)   
        
    @score(category="MODES")
    def test_channel_mode17(self):
        clients = self._clients_connect(10, join_channel = "#test")
        
        nick1, client1 = clients[0]  
        
        self._channel_mode(client1, nick1, "#test", "+m")
                
        for nick, client in clients:
            self._test_relayed_mode(client, from_nick=nick1, channel="#test", mode="+m")        
            
    @score(category="MODES")
    def test_channel_mode18(self):
        clients = self._clients_connect(2, join_channel = "#test")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1]  
        
        self._channel_mode(client2, nick2, "#test", "+m", expect_ops_needed = True)
        
    
    @score(category="MODES")
    def test_channeluser_mode1(self):
        client1 = self._connect_user("user1", "User One")
        
        self._channel_mode(client1, "user1", "#test", "+v", "user2", expect_wrong_channel = True)       

    @score(category="MODES")
    def test_channeluser_mode2(self):
        client1 = self._connect_user("user1", "User One")

        client1.send_cmd("JOIN #test")
        self._test_join(client1, "user1", "#test")  

        client2 = self._connect_user("user2", "User Two")
        
        self._channel_mode(client2, "user2", "#test", "+v", "user1", expect_ops_needed = True)      
        
    @score(category="MODES")
    def test_channeluser_mode3(self):
        clients = self._clients_connect(2, join_channel = "#test")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1]  
        
        self._channel_mode(client2, nick2, "#test", "+v", "user1", expect_ops_needed = True)    
        
    @score(category="MODES")
    def test_channeluser_mode4(self):
        clients = self._clients_connect(2, join_channel = "#test")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1]  
        
        self._channel_mode(client1, nick1, "#test", "+v", "user3", expect_not_on_channel = True)      
        
    @score(category="MODES")
    def test_channeluser_mode5(self):
        client1 = self._connect_user("user1", "User One")

        client1.send_cmd("JOIN #test")
        self._test_join(client1, "user1", "#test")  

        client2 = self._connect_user("user2", "User Two")
        
        self._channel_mode(client1, "user1", "#test", "+v", "user2", expect_not_on_channel = True)   
        
    @score(category="MODES")
    def test_channeluser_mode6(self):
        clients = self._clients_connect(2, join_channel = "#test")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1]  
        
        self._channel_mode(client1, nick1, "#test", "+t", "user2", expect_wrong_mode = True)                             
         
    @score(category="MODES")
    def test_channeluser_mode7(self):
        clients = self._clients_connect(2, join_channel = "#test")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1]  
        
        self._channel_mode(client1, nick1, "#test", "+m", "user2", expect_wrong_mode = True)     
        
        
    @score(category="MODES")
    def test_channeluser_mode8(self):
        clients = self._clients_connect(10, join_channel = "#test")
        
        nick1, client1 = clients[0]  
        
        self._channel_mode(client1, nick1, "#test", "+v", "user2")
                
        for nick, client in clients:
            self._test_relayed_mode(client, from_nick=nick1, channel="#test", mode="+v", mode_nick="user2")                                   
        
    @score(category="MODES")
    def test_channeluser_mode9(self):
        clients = self._clients_connect(10, join_channel = "#test")
        
        nick1, client1 = clients[0]  
        
        self._channel_mode(client1, nick1, "#test", "+o", "user2")
                
        for nick, client in clients:
            self._test_relayed_mode(client, from_nick=nick1, channel="#test", mode="+o", mode_nick="user2")                                   

    @score(category="MODES")
    def test_channeluser_mode10(self):
        clients = self._clients_connect(5, join_channel = "#test")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1]  
        
        self._channel_mode(client1, nick1, "#test", "+o", "user2")
        for nick, client in clients:
            self._test_relayed_mode(client, from_nick=nick1, channel="#test", mode="+o", mode_nick="user2")                                   

        self._channel_mode(client2, nick2, "#test", "+v", "user3")
        for nick, client in clients:
            self._test_relayed_mode(client, from_nick=nick2, channel="#test", mode="+v", mode_nick="user3")                                   

        self._channel_mode(client1, nick1, "#test", "-o", "user2")
        for nick, client in clients:
            self._test_relayed_mode(client, from_nick=nick1, channel="#test", mode="-o", mode_nick="user2")                                   

        self._channel_mode(client2, nick2, "#test", "+v", "user4", expect_ops_needed=True)
    
    @score(category="MODES")
    def test_connect_channels1(self):
        self._channels_connect(channels1)
        
    @score(category="MODES")
    def test_connect_channels2(self):
        self._channels_connect(channels2)

    @score(category="MODES")
    def test_connect_channels3(self):
        self._channels_connect(channels3)

                   
class Permissions(ChircTestCase):
                        
    def _join_and_mode(self, numclients, channel, mode):
        clients = self._clients_connect(numclients, join_channel = channel)
        
        nick1, client1 = clients[0]  
        
        self._channel_mode(client1, nick1, channel, mode)        

        for nick, client in clients:
            self._test_relayed_mode(client, from_nick=nick1, channel=channel, mode=mode)   
            
        return clients  
    
    def _privmsg(self, client, nick, channel, clients):
        client.send_cmd("PRIVMSG %s :Hello from %s!" % (channel,nick))
        for (nick2, client2) in clients:
            if nick != nick2:
                self._test_relayed_privmsg(client2, from_nick=nick, recip=channel, msg="Hello from %s!" % nick)  
                  
    def _oper(self, client, nick):
        client.send_cmd("OPER %s %s" % (nick, OPER_PASSWD))
        
        reply = self.get_reply(client, expect_code = replies.RPL_YOUREOPER, expect_nick = nick, 
                               expect_nparams = 1,
                               long_param_re = "You are now an IRC operator")                                 
                        
    @score(category="MODES")
    def test_permissions_privmsg1(self):
        clients = self._join_and_mode(3, "#test", "+m")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1]  
        
        client2.send_cmd("PRIVMSG #test :Hello from %s!" % nick2)
        
        self.get_reply(client2, expect_code = replies.ERR_CANNOTSENDTOCHAN, expect_nick = nick2, 
                       expect_nparams = 2, expect_short_params = ["#test"],
                       long_param_re = "Cannot send to channel")           
        
    @score(category="MODES")
    def test_permissions_privmsg2(self):
        clients = self._join_and_mode(3, "#test", "+m")
        
        nick1, client1 = clients[0]  
        
        self._privmsg(client1, nick1, "#test", clients)
        
    @score(category="MODES")
    def test_permissions_privmsg3(self):
        clients = self._join_and_mode(3, "#test", "+m")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1] 
        
        self._channel_mode(client1, nick1, "#test", "+v", nick2)     
        for nick, client in clients:
            self._test_relayed_mode(client, from_nick=nick1, channel="#test", mode="+v", mode_nick=nick2)                                   

        self._privmsg(client2, nick2, "#test", clients)        
        
    @score(category="MODES")
    def test_permissions_privmsg4(self):
        clients = self._join_and_mode(3, "#test", "+m")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1] 
        
        self._channel_mode(client1, nick1, "#test", "+o", nick2)       
        for nick, client in clients:
            self._test_relayed_mode(client, from_nick=nick1, channel="#test", mode="+o", mode_nick=nick2)                                   
        
        self._privmsg(client2, nick2, "#test", clients)   
        
    @score(category="MODES")
    def test_permissions_privmsg5(self):
        clients = self._join_and_mode(3, "#test", "+m")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1] 
        
        self._channel_mode(client1, nick1, "#test", "+v", nick2)       
        for nick, client in clients:
            self._test_relayed_mode(client, from_nick=nick1, channel="#test", mode="+v", mode_nick=nick2)                                   
        
        self._channel_mode(client1, nick1, "#test", "-v", nick2)       
        for nick, client in clients:
            self._test_relayed_mode(client, from_nick=nick1, channel="#test", mode="-v", mode_nick=nick2)                                   
        
        client2.send_cmd("PRIVMSG #test :Hello from %s!" % nick2)
        
        self.get_reply(client2, expect_code = replies.ERR_CANNOTSENDTOCHAN, expect_nick = nick2, 
                       expect_nparams = 2, expect_short_params = ["#test"],
                       long_param_re = "Cannot send to channel")                
        
        
    @score(category="MODES")
    def test_permissions_notice(self):
        clients = self._join_and_mode(3, "#test", "+m")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1]  
        
        client2.send_cmd("NOTICE #test :Hello from %s!" % nick2)
        
        self.assertRaises(ReplyTimeoutException, self.get_reply, client2) 
        
        
    @score(category="MODES")
    def test_permissions_topic1(self):
        clients = self._join_and_mode(3, "#test", "+t")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1]  
        
        client2.send_cmd("TOPIC #test :Hello")
        
        self.get_reply(client2, expect_code = replies.ERR_CHANOPRIVSNEEDED, expect_nick = nick2, 
                   expect_nparams = 2, expect_short_params = ["#test"],
                   long_param_re = "You're not channel operator")       
        
    @score(category="MODES")
    def test_permissions_topic2(self):
        clients = self._join_and_mode(3, "#test", "+t")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1] 
        
        self._channel_mode(client1, nick1, "#test", "+o", nick2)       
        for nick, client in clients:
            self._test_relayed_mode(client, from_nick=nick1, channel="#test", mode="+o", mode_nick=nick2)                                   
        
        client2.send_cmd("TOPIC #test :Hello")
        for nick, client in clients:
            self._test_relayed_topic(client, from_nick=nick2, channel="#test", topic="Hello")            

           
    @score(category="MODES")
    def test_permissions_oper1(self):
        clients = self._clients_connect(3, join_channel = "#test")
        
        nick2, client2 = clients[1] 
        
        self._oper(client2, nick2)
        
        self._channel_mode(client2, nick2, "#test", "+m")
                
        for nick, client in clients:
            self._test_relayed_mode(client, from_nick=nick2, channel="#test", mode="+m")                
           
        
    @score(category="MODES")
    def test_permissions_oper2(self):
        clients = self._clients_connect(3, join_channel = "#test")
        
        nick2, client2 = clients[1] 
        
        self._oper(client2, nick2)
        
        self._channel_mode(client2, nick2, "#test", "+v", "user3")
                
        for nick, client in clients:
            self._test_relayed_mode(client, from_nick=nick2, channel="#test", mode="+v", mode_nick="user3")                                   
        
    @score(category="MODES")
    def test_permissions_oper3(self):
        clients = self._clients_connect(3, join_channel = "#test")
        
        nick2, client2 = clients[1] 
        
        self._oper(client2, nick2)
        
        self._channel_mode(client2, nick2, "#test", "+o", "user3")
                
        for nick, client in clients:
            self._test_relayed_mode(client, from_nick=nick2, channel="#test", mode="+o", mode_nick="user3")                                   
        
           
    @score(category="MODES")
    def test_permissions_oper4(self):
        clients = self._join_and_mode(3, "#test", "+m")
        
        nick2, client2 = clients[1] 
        
        self._oper(client2, nick2)

        self._privmsg(client2, nick2, "#test", clients)        
        
    @score(category="MODES")
    def test_permissions_oper5(self):
        clients = self._join_and_mode(3, "#test", "+m")
        
        nick2, client2 = clients[1] 
        
        self._oper(client2, nick2)
        
        self._privmsg(client2, nick2, "#test", clients)              

    @score(category="MODES")
    def test_permissions_oper6(self):
        clients = self._join_and_mode(3, "#test", "+t")
        
        nick2, client2 = clients[1] 
        
        self._oper(client2, nick2)
                
        client2.send_cmd("TOPIC #test :Hello")
        for nick, client in clients:
            self._test_relayed_topic(client, from_nick=nick2, channel="#test", topic="Hello")        
            
            
class AWAY(ChircTestCase):       
    def _away(self, client, nick, msg):
        client.send_cmd("AWAY :%s" % msg)
        self.get_reply(client, expect_code = replies.RPL_NOWAWAY, expect_nick = nick,
                       expect_nparams = 1, long_param_re = "You have been marked as being away")    

    def _unaway(self, client, nick):
        client.send_cmd("AWAY")
        self.get_reply(client, expect_code = replies.RPL_UNAWAY, expect_nick = nick,
                       expect_nparams = 1, long_param_re = "You are no longer marked as being away")    
    
    @score(category="AWAY")
    def test_away1(self):
        client1 = self._connect_user("user1", "User One")
        
        self._away(client1, "user1", "I'm not here")
        
    @score(category="AWAY")
    def test_away2(self):
        client1 = self._connect_user("user1", "User One")
        
        self._away(client1, "user1", "I'm not here")
        self._unaway(client1, "user1")
        
    @score(category="AWAY")
    def test_away3(self):
        client1 = self._connect_user("user1", "User One")
        
        self._unaway(client1, "user1")
        
    @score(category="AWAY")
    def test_away4(self):
        clients = self._clients_connect(2)
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1]          

        away_msg = "I'm not here"

        self._away(client1, "user1", away_msg)
        
        client2.send_cmd("PRIVMSG user1 :Hello")
        
        self.get_reply(client2, expect_code = replies.RPL_AWAY, expect_nick = nick2,
                       expect_nparams = 2, expect_short_params = ["user1"],
                       long_param_re = away_msg)           

    @score(category="AWAY")
    def test_away5(self):
        clients = self._clients_connect(2)
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1]          

        away_msg = "I'm not here"

        self._away(client1, "user1", away_msg)
        
        client2.send_cmd("NOTICE user1 :Hello")
        
        self.assertRaises(ReplyTimeoutException, self.get_reply, client2)      
        
    @score(category="AWAY")
    def test_away6(self):
        clients = self._clients_connect(2, join_channel = "#test")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1]          

        away_msg = "I'm not here"

        self._away(client1, "user1", away_msg)
        
        client2.send_cmd("PRIVMSG #test :Hello")
        self._test_relayed_privmsg(client1, from_nick=nick2, recip="#test", msg="Hello")
        self.assertRaises(ReplyTimeoutException, self.get_reply, client2)                   


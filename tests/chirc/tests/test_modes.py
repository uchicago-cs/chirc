import pytest
from chirc.tests.fixtures import channels1, channels2, channels3
from chirc import replies
from chirc.types import ReplyTimeoutException

@pytest.mark.category("OPER")
class TestOPER(object):

    def test_oper1(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("OPER user1 %s" % irc_session.oper_password)
        
        reply = irc_session.get_reply(client1, expect_code = replies.RPL_YOUREOPER, expect_nick = "user1", 
                               expect_nparams = 1,
                               long_param_re = "You are now an IRC operator")      
        
    def test_oper2(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("OPER user1 BAD%s" % irc_session.oper_password)
        
        reply = irc_session.get_reply(client1, expect_code = replies.ERR_PASSWDMISMATCH, expect_nick = "user1", 
                               expect_nparams = 1,
                               long_param_re = "Password incorrect")

@pytest.mark.category("MODES")        
class TestMODE(object):       
     
    def test_user_mode1(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        irc_session.set_user_mode(client1, "user1", "user1", "+o", expect_relay=False)
    
    def test_user_mode2(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        irc_session.set_user_mode(client1, "user1", "user1", "-o")

    def test_user_mode3(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        irc_session.set_user_mode(client1, "user1", "user1", "+a", expect_relay=False)

    def test_user_mode4(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        irc_session.set_user_mode(client1, "user1", "user1", "-a", expect_relay=False)
        
    def test_user_mode5(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        irc_session.set_user_mode(client1, "user1", "user1", "+v", expect_wrong_mode=True)
        
    def test_user_mode6(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        irc_session.set_user_mode(client1, "user1", "user1", "-v", expect_wrong_mode=True)
        
    def test_user_mode7(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        irc_session.set_user_mode(client1, "user1", "user1", "+t", expect_wrong_mode=True)
        
    def test_user_mode8(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        irc_session.set_user_mode(client1, "user1", "user1", "-t", expect_wrong_mode=True)        
        
    def test_user_mode9(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        irc_session.set_user_mode(client1, "user1", "user1", "+z", expect_wrong_mode=True)
        
    def test_user_mode10(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        irc_session.set_user_mode(client1, "user1", "user1", "-z", expect_wrong_mode=True)        
        
    def test_user_mode11(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        irc_session.set_user_mode(client1, "user1", "user2", "-o")   

    def test_user_mode12(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        irc_session.set_user_mode(client1, "user1", "user2", "-z")   
        

    def test_channel_mode1(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, "user1", "#test")
        
        irc_session.set_channel_mode(client1, "user1", "#test", "+m")
        irc_session.verify_relayed_mode(client1, "user1", "#test", "+m")
        
    def test_channel_mode2(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, "user1", "#test")
        
        irc_session.set_channel_mode(client1, "user1", "#test", "+t")
        irc_session.verify_relayed_mode(client1, "user1", "#test", "+t")        
        
    def test_channel_mode3(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, "user1", "#test")
        
        irc_session.set_channel_mode(client1, "user1", "#test", "-m")
        irc_session.verify_relayed_mode(client1, "user1", "#test", "-m")
        
    def test_channel_mode4(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, "user1", "#test")
        
        irc_session.set_channel_mode(client1, "user1", "#test", "-t")
        irc_session.verify_relayed_mode(client1, "user1", "#test", "-t")
        
    def test_channel_mode5(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, "user1", "#test")
        
        irc_session.set_channel_mode(client1, "user1", "#test", "+z", expect_wrong_mode=True)               
        
    def test_channel_mode6(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, "user1", "#test")
        
        irc_session.set_channel_mode(client1, "user1", "#test", "+o", expect_wrong_mode=True)             
        
    def test_channel_mode7(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, "user1", "#test")
        
        irc_session.set_channel_mode(client1, "user1", "#test", "+v", expect_wrong_mode=True)        
        
    def test_channel_mode8(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, "user1", "#test")
        
        irc_session.set_channel_mode(client1, "user1", "#test", "+m")
        irc_session.verify_relayed_mode(client1, "user1", "#test", "+m")      
        
        irc_session.set_channel_mode(client1, "user1", "#test", expect_mode = "m")
        
    def test_channel_mode9(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, "user1", "#test")
        
        irc_session.set_channel_mode(client1, "user1", "#test", "+m")
        irc_session.verify_relayed_mode(client1, "user1", "#test", "+m")      

        irc_session.set_channel_mode(client1, "user1", "#test", "+t")
        irc_session.verify_relayed_mode(client1, "user1", "#test", "+t")      
        
        irc_session.set_channel_mode(client1, "user1", "#test", expect_mode = "mt")           
        
    def test_channel_mode10(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, "user1", "#test")
        
        irc_session.set_channel_mode(client1, "user1", "#test", "+m")
        irc_session.verify_relayed_mode(client1, "user1", "#test", "+m")      

        irc_session.set_channel_mode(client1, "user1", "#test", "+t")
        irc_session.verify_relayed_mode(client1, "user1", "#test", "+t")      

        irc_session.set_channel_mode(client1, "user1", "#test", "-t")
        irc_session.verify_relayed_mode(client1, "user1", "#test", "-t")      
        
        irc_session.set_channel_mode(client1, "user1", "#test", expect_mode = "m")                 
    
    def test_channel_mode11(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, "user1", "#test")
        
        irc_session.set_channel_mode(client1, "user1", "#test", "+m")
        irc_session.verify_relayed_mode(client1, "user1", "#test", "+m")      

        irc_session.set_channel_mode(client1, "user1", "#test", "+t")
        irc_session.verify_relayed_mode(client1, "user1", "#test", "+t")      

        irc_session.set_channel_mode(client1, "user1", "#test", "-m")
        irc_session.verify_relayed_mode(client1, "user1", "#test", "-m")      
        
        irc_session.set_channel_mode(client1, "user1", "#test", expect_mode = "t")    
        
    def test_channel_mode12(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, "user1", "#test")
        
        irc_session.set_channel_mode(client1, "user1", "#test", "+m")
        irc_session.verify_relayed_mode(client1, "user1", "#test", "+m")      

        irc_session.set_channel_mode(client1, "user1", "#test", "+t")
        irc_session.verify_relayed_mode(client1, "user1", "#test", "+t")      

        irc_session.set_channel_mode(client1, "user1", "#test", "-m")
        irc_session.verify_relayed_mode(client1, "user1", "#test", "-m")      

        irc_session.set_channel_mode(client1, "user1", "#test", "-t")
        irc_session.verify_relayed_mode(client1, "user1", "#test", "-t")      
        
        irc_session.set_channel_mode(client1, "user1", "#test", expect_mode = "")         
        

    def test_channel_mode13(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, "user1", "#test")  
        
        irc_session.set_channel_mode(client1, "user1", "#test", expect_mode = "")       
        

    def test_channel_mode14(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        irc_session.set_channel_mode(client1, "user1", "#test", expect_wrong_channel = True)      
        

    def test_channel_mode15(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        irc_session.set_channel_mode(client1, "user1", "#test", "+m", expect_wrong_channel = True)      
        

    def test_channel_mode16(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        irc_session.set_channel_mode(client1, "user1", "#test", "+o", expect_wrong_channel = True)   
        

    def test_channel_mode17(self, irc_session):
        clients = irc_session.connect_clients(10, join_channel = "#test")
        
        nick1, client1 = clients[0]  
        
        irc_session.set_channel_mode(client1, nick1, "#test", "+m")
                
        for nick, client in clients:
            irc_session.verify_relayed_mode(client, from_nick=nick1, channel="#test", mode="+m")        
            

    def test_channel_mode18(self, irc_session):
        clients = irc_session.connect_clients(2, join_channel = "#test")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1]  
        
        irc_session.set_channel_mode(client2, nick2, "#test", "+m", expect_ops_needed = True)
        
    

    def test_channeluser_mode1(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        irc_session.set_channel_mode(client1, "user1", "#test", "+v", "user2", expect_wrong_channel = True)       


    def test_channeluser_mode2(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")

        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, "user1", "#test")  

        client2 = irc_session.connect_user("user2", "User Two")
        
        irc_session.set_channel_mode(client2, "user2", "#test", "+v", "user1", expect_ops_needed = True)      
        

    def test_channeluser_mode3(self, irc_session):
        clients = irc_session.connect_clients(2, join_channel = "#test")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1]  
        
        irc_session.set_channel_mode(client2, nick2, "#test", "+v", "user1", expect_ops_needed = True)    
        

    def test_channeluser_mode4(self, irc_session):
        clients = irc_session.connect_clients(2, join_channel = "#test")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1]  
        
        irc_session.set_channel_mode(client1, nick1, "#test", "+v", "user3", expect_not_on_channel = True)      
        

    def test_channeluser_mode5(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")

        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, "user1", "#test")  

        client2 = irc_session.connect_user("user2", "User Two")
        
        irc_session.set_channel_mode(client1, "user1", "#test", "+v", "user2", expect_not_on_channel = True)   
        

    def test_channeluser_mode6(self, irc_session):
        clients = irc_session.connect_clients(2, join_channel = "#test")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1]  
        
        irc_session.set_channel_mode(client1, nick1, "#test", "+t", "user2", expect_wrong_mode = True)                             
         

    def test_channeluser_mode7(self, irc_session):
        clients = irc_session.connect_clients(2, join_channel = "#test")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1]  
        
        irc_session.set_channel_mode(client1, nick1, "#test", "+m", "user2", expect_wrong_mode = True)     
        
        

    def test_channeluser_mode8(self, irc_session):
        clients = irc_session.connect_clients(10, join_channel = "#test")
        
        nick1, client1 = clients[0]  
        
        irc_session.set_channel_mode(client1, nick1, "#test", "+v", "user2")
                
        for nick, client in clients:
            irc_session.verify_relayed_mode(client, from_nick=nick1, channel="#test", mode="+v", mode_nick="user2")                                   
        

    def test_channeluser_mode9(self, irc_session):
        clients = irc_session.connect_clients(10, join_channel = "#test")
        
        nick1, client1 = clients[0]  
        
        irc_session.set_channel_mode(client1, nick1, "#test", "+o", "user2")
                
        for nick, client in clients:
            irc_session.verify_relayed_mode(client, from_nick=nick1, channel="#test", mode="+o", mode_nick="user2")                                   


    def test_channeluser_mode10(self, irc_session):
        clients = irc_session.connect_clients(5, join_channel = "#test")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1]  
        
        irc_session.set_channel_mode(client1, nick1, "#test", "+o", "user2")
        for nick, client in clients:
            irc_session.verify_relayed_mode(client, from_nick=nick1, channel="#test", mode="+o", mode_nick="user2")                                   

        irc_session.set_channel_mode(client2, nick2, "#test", "+v", "user3")
        for nick, client in clients:
            irc_session.verify_relayed_mode(client, from_nick=nick2, channel="#test", mode="+v", mode_nick="user3")                                   

        irc_session.set_channel_mode(client1, nick1, "#test", "-o", "user2")
        for nick, client in clients:
            irc_session.verify_relayed_mode(client, from_nick=nick1, channel="#test", mode="-o", mode_nick="user2")                                   

        irc_session.set_channel_mode(client2, nick2, "#test", "+v", "user4", expect_ops_needed=True)
    

    def test_connect_channels1(self, irc_session):
        irc_session.connect_and_join_channels(channels1)
        

    def test_connect_channels2(self, irc_session):
        irc_session.connect_and_join_channels(channels2)


    def test_connect_channels3(self, irc_session):
        irc_session.connect_and_join_channels(channels3)

@pytest.mark.category("MODES")        
class TestPermissions(object):
                        
    def _join_and_mode(self, irc_session, numclients, channel, mode):
        clients = irc_session.connect_clients(numclients, join_channel = channel)
        
        nick1, client1 = clients[0]  
        
        irc_session.set_channel_mode(client1, nick1, channel, mode)        

        for nick, client in clients:
            irc_session.verify_relayed_mode(client, from_nick=nick1, channel=channel, mode=mode)   
            
        return clients  
    
    def _privmsg(self, irc_session, client, nick, channel, clients):
        client.send_cmd("PRIVMSG %s :Hello from %s!" % (channel,nick))
        for (nick2, client2) in clients:
            if nick != nick2:
                irc_session.verify_relayed_privmsg(client2, from_nick=nick, recip=channel, msg="Hello from %s!" % nick)  
                  
    def _oper(self, irc_session, client, nick):
        client.send_cmd("OPER %s %s" % (nick, irc_session.oper_password))
        
        reply = irc_session.get_reply(client, expect_code = replies.RPL_YOUREOPER, expect_nick = nick, 
                               expect_nparams = 1,
                               long_param_re = "You are now an IRC operator")                                 
                        

    def test_permissions_privmsg1(self, irc_session):
        clients = self._join_and_mode(irc_session, 3, "#test", "+m")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1]  
        
        client2.send_cmd("PRIVMSG #test :Hello from %s!" % nick2)
        
        irc_session.get_reply(client2, expect_code = replies.ERR_CANNOTSENDTOCHAN, expect_nick = nick2, 
                       expect_nparams = 2, expect_short_params = ["#test"],
                       long_param_re = "Cannot send to channel")           
        

    def test_permissions_privmsg2(self, irc_session):
        clients = self._join_and_mode(irc_session, 3, "#test", "+m")
        
        nick1, client1 = clients[0]  
        
        self._privmsg(irc_session, client1, nick1, "#test", clients)
        

    def test_permissions_privmsg3(self, irc_session):
        clients = self._join_and_mode(irc_session, 3, "#test", "+m")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1] 
        
        irc_session.set_channel_mode(client1, nick1, "#test", "+v", nick2)     
        for nick, client in clients:
            irc_session.verify_relayed_mode(client, from_nick=nick1, channel="#test", mode="+v", mode_nick=nick2)                                   

        self._privmsg(irc_session, client2, nick2, "#test", clients)        
        

    def test_permissions_privmsg4(self, irc_session):
        clients = self._join_and_mode(irc_session, 3, "#test", "+m")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1] 
        
        irc_session.set_channel_mode(client1, nick1, "#test", "+o", nick2)       
        for nick, client in clients:
            irc_session.verify_relayed_mode(client, from_nick=nick1, channel="#test", mode="+o", mode_nick=nick2)                                   
        
        self._privmsg(irc_session, client2, nick2, "#test", clients)   
        

    def test_permissions_privmsg5(self, irc_session):
        clients = self._join_and_mode(irc_session, 3, "#test", "+m")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1] 
        
        irc_session.set_channel_mode(client1, nick1, "#test", "+v", nick2)       
        for nick, client in clients:
            irc_session.verify_relayed_mode(client, from_nick=nick1, channel="#test", mode="+v", mode_nick=nick2)                                   
        
        irc_session.set_channel_mode(client1, nick1, "#test", "-v", nick2)       
        for nick, client in clients:
            irc_session.verify_relayed_mode(client, from_nick=nick1, channel="#test", mode="-v", mode_nick=nick2)                                   
        
        client2.send_cmd("PRIVMSG #test :Hello from %s!" % nick2)
        
        irc_session.get_reply(client2, expect_code = replies.ERR_CANNOTSENDTOCHAN, expect_nick = nick2, 
                       expect_nparams = 2, expect_short_params = ["#test"],
                       long_param_re = "Cannot send to channel")                
        
        

    def test_permissions_notice(self, irc_session):
        clients = self._join_and_mode(irc_session, 3, "#test", "+m")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1]  
        
        client2.send_cmd("NOTICE #test :Hello from %s!" % nick2)
        
        with pytest.raises(ReplyTimeoutException):
            irc_session.get_reply(client2)                 
        

    def test_permissions_topic1(self, irc_session):
        clients = self._join_and_mode(irc_session, 3, "#test", "+t")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1]  
        
        client2.send_cmd("TOPIC #test :Hello")
        
        irc_session.get_reply(client2, expect_code = replies.ERR_CHANOPRIVSNEEDED, expect_nick = nick2, 
                   expect_nparams = 2, expect_short_params = ["#test"],
                   long_param_re = "You're not channel operator")       
        

    def test_permissions_topic2(self, irc_session):
        clients = self._join_and_mode(irc_session, 3, "#test", "+t")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1] 
        
        irc_session.set_channel_mode(client1, nick1, "#test", "+o", nick2)       
        for nick, client in clients:
            irc_session.verify_relayed_mode(client, from_nick=nick1, channel="#test", mode="+o", mode_nick=nick2)                                   
        
        client2.send_cmd("TOPIC #test :Hello")
        for nick, client in clients:
            irc_session.verify_relayed_topic(client, from_nick=nick2, channel="#test", topic="Hello")            

           

    def test_permissions_oper1(self, irc_session):
        clients = irc_session.connect_clients(3, join_channel = "#test")
        
        nick2, client2 = clients[1] 
        
        self._oper(irc_session, client2, nick2)
        
        irc_session.set_channel_mode(client2, nick2, "#test", "+m")
                
        for nick, client in clients:
            irc_session.verify_relayed_mode(client, from_nick=nick2, channel="#test", mode="+m")                
           
        

    def test_permissions_oper2(self, irc_session):
        clients = irc_session.connect_clients(3, join_channel = "#test")
        
        nick2, client2 = clients[1] 
        
        self._oper(irc_session, client2, nick2)
        
        irc_session.set_channel_mode(client2, nick2, "#test", "+v", "user3")
                
        for nick, client in clients:
            irc_session.verify_relayed_mode(client, from_nick=nick2, channel="#test", mode="+v", mode_nick="user3")                                   
        

    def test_permissions_oper3(self, irc_session):
        clients = irc_session.connect_clients(3, join_channel = "#test")
        
        nick2, client2 = clients[1] 
        
        self._oper(irc_session, client2, nick2)
        
        irc_session.set_channel_mode(client2, nick2, "#test", "+o", "user3")
                
        for nick, client in clients:
            irc_session.verify_relayed_mode(client, from_nick=nick2, channel="#test", mode="+o", mode_nick="user3")                                   
        
           

    def test_permissions_oper4(self, irc_session):
        clients = self._join_and_mode(irc_session, 3, "#test", "+m")
        
        nick2, client2 = clients[1] 
        
        self._oper(irc_session, client2, nick2)

        self._privmsg(irc_session, client2, nick2, "#test", clients)        
        

    def test_permissions_oper5(self, irc_session):
        clients = self._join_and_mode(irc_session, 3, "#test", "+m")
        
        nick2, client2 = clients[1] 
        
        self._oper(irc_session, client2, nick2)
        
        self._privmsg(irc_session, client2, nick2, "#test", clients)              


    def test_permissions_oper6(self, irc_session):
        clients = self._join_and_mode(irc_session, 3, "#test", "+t")
        
        nick2, client2 = clients[1] 
        
        self._oper(irc_session, client2, nick2)
                
        client2.send_cmd("TOPIC #test :Hello")
        for nick, client in clients:
            irc_session.verify_relayed_topic(client, from_nick=nick2, channel="#test", topic="Hello")        
            

@pytest.mark.category("AWAY")
class TestAWAY(object):       
    def _away(self, irc_session, client, nick, msg):
        client.send_cmd("AWAY :%s" % msg)
        irc_session.get_reply(client, expect_code = replies.RPL_NOWAWAY, expect_nick = nick,
                       expect_nparams = 1, long_param_re = "You have been marked as being away")    

    def _unaway(self, irc_session, client, nick):
        client.send_cmd("AWAY")
        irc_session.get_reply(client, expect_code = replies.RPL_UNAWAY, expect_nick = nick,
                       expect_nparams = 1, long_param_re = "You are no longer marked as being away")    
    
    def test_away1(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        self._away(irc_session, client1, "user1", "I'm not here")
        
    def test_away2(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        self._away(irc_session, client1, "user1", "I'm not here")
        self._unaway(irc_session, client1, "user1")
        
    def test_away3(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        self._unaway(irc_session, client1, "user1")
        
    def test_away4(self, irc_session):
        clients = irc_session.connect_clients(2)
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1]          

        away_msg = "I'm not here"

        self._away(irc_session, client1, "user1", away_msg)
        
        client2.send_cmd("PRIVMSG user1 :Hello")
        
        irc_session.get_reply(client2, expect_code = replies.RPL_AWAY, expect_nick = nick2,
                       expect_nparams = 2, expect_short_params = ["user1"],
                       long_param_re = away_msg)           

    def test_away5(self, irc_session):
        clients = irc_session.connect_clients(2)
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1]          

        away_msg = "I'm not here"

        self._away(irc_session, client1, "user1", away_msg)
        
        client2.send_cmd("NOTICE user1 :Hello")
        
        with pytest.raises(ReplyTimeoutException):
            irc_session.get_reply(client2)         
        
                
    def test_away6(self, irc_session):
        clients = irc_session.connect_clients(2, join_channel = "#test")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1]          

        away_msg = "I'm not here"

        self._away(irc_session, client1, "user1", away_msg)
        
        client2.send_cmd("PRIVMSG #test :Hello")
        irc_session.verify_relayed_privmsg(client1, from_nick=nick2, recip="#test", msg="Hello")
        with pytest.raises(ReplyTimeoutException):
            irc_session.get_reply(client2)                   


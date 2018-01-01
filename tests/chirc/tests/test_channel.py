import pytest
from chirc.tests.fixtures import channels1, channels2, channels3, channels4
from chirc import replies

@pytest.mark.category("CHANNEL_JOIN")
class TestJOIN(object):


    def test_join1(self, irc_session):
        """
        A single user connects to the server and joins a channel
        that does not already exist.
        """
        
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        
        irc_session.verify_join(client1, "user1", "#test")
        

    def test_join2(self, irc_session):
        """
        A single user connects to the server and joins a channel
        that does not already exist. The user tries to join it again,
        which results in no reply.
        """
        
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        
        irc_session.verify_join(client1, "user1", "#test")

        client1.send_cmd("JOIN #test")
        irc_session.get_reply(client1, expect_timeout = True)
        

    def test_join3(self, irc_session):
        """
        Five clients connect to the server and join the same channel
        """
        
        clients = irc_session.connect_clients(5)

        for (nick, client) in clients:
            client.send_cmd("JOIN #test")
            irc_session.verify_join(client, nick, "#test")        
        

    def test_join4(self, irc_session):
        """
        Two clients connect to the server, one joins a channel
        (that does not previously exist) first, and the other
        one joins it after that.
        """        
        
        client1 = irc_session.connect_user("user1", "User One")
        client2 = irc_session.connect_user("user2", "User Two")
        
        client1.send_cmd("JOIN #test")
        
        irc_session.verify_join(client1, "user1", "#test")

        client2.send_cmd("JOIN #test")
        irc_session.verify_join(client2, "user2", "#test")
        
        irc_session.verify_relayed_join(client1, from_nick="user2", channel="#test")
        

    def test_join5(self, irc_session):
        """
        Five clients connect to the server and all join the same channel.
        We verify that the JOINs are correctly relayed in the channel.
        """
        
        clients = irc_session.connect_clients(5)

        for (nick, client) in clients:
            client.send_cmd("JOIN #test")
            irc_session.verify_join(client, nick, "#test")  
            
        relayed = len(clients) - 1
        for (nick, client) in clients:
            for i in range(relayed):
                irc_session.verify_relayed_join(client, from_nick = None, channel="#test")
            relayed -= 1
        
    
    def test_join_params(self, irc_session):
        """
        Test ERR_NEEDMOREPARAMS reply
        """
        
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("JOIN")
        
        irc_session.get_ERR_NEEDMOREPARAMS_reply(client1, 
                                                 expect_nick="user1", expect_cmd="JOIN")


@pytest.mark.category("CHANNEL_PRIVMSG_NOTICE")
class TestChannelPRIVMSG(object):
    
    def _test_join_and_privmsg(self, irc_session, numclients):
        """
        Connect `numclients` to the server, join the same channel,
        and have each of them send a PRIVMSG to the channel (and
        verify it is relayed correctly to everyone else in the channel
        """
        
        clients = irc_session.connect_clients(numclients, join_channel = "#test")
        
        for (nick1, client1) in clients:
            client1.send_cmd("PRIVMSG #test :Hello from %s!" % nick1)
            for (nick2, client2) in clients:
                if nick1 != nick2:
                    irc_session.verify_relayed_privmsg(client2, from_nick=nick1, recip="#test", msg="Hello from %s!" % nick1)  
    

    def test_channel_privmsg1(self, irc_session):
        """
        Two clients connect to the server, join the same channel,
        and send a PRIVMSG to the channel.
        """
        self._test_join_and_privmsg(irc_session, 2)
        

    def test_channel_privmsg2(self, irc_session):
        """
        Five clients connect to the server, join the same channel,
        and send a PRIVMSG to the channel.
        """
        self._test_join_and_privmsg(irc_session, 5)


    def test_channel_privmsg3(self, irc_session):
        """
        Twenty clients connect to the server, join the same channel,
        and send a PRIVMSG to the channel.
        """
        self._test_join_and_privmsg(irc_session, 20)
        

    def test_channel_privmsg_nochannel(self, irc_session):
        """
        A user connects to the server and sends a message to
        a channel that doesn't exist
        """
        
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("PRIVMSG #test :Hello")

        reply = irc_session.get_reply(client1, expect_code = replies.ERR_NOSUCHNICK, expect_nick = "user1", 
                               expect_nparams = 2, expect_short_params = ["#test"],
                               long_param_re = "No such nick/channel")    
        

    def test_channel_privmsg_notonchannel(self, irc_session):
        """
        Two clients connect to the server. One joins #test, and the other
        one tries to send a message to #test.
        """
        
        client1 = irc_session.connect_user("user1", "User One")

        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, "user1", "#test")  

        client2 = irc_session.connect_user("user2", "User Two")  
        client2.send_cmd("PRIVMSG #test :Hello")      
        
        irc_session.get_reply(client2, expect_code = replies.ERR_CANNOTSENDTOCHAN, expect_nick = "user2", 
                       expect_nparams = 2, expect_short_params = ["#test"],
                       long_param_re = "Cannot send to channel")          
          

@pytest.mark.category("CHANNEL_PRIVMSG_NOTICE")        
class TestChannelNOTICE(object):     
    

    def test_channel_notice_nochannel(self, irc_session):
        """
        A client connects to the server and sends a NOTICE to a channel
        that does not exist.
        """
        
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("NOTICE #test :Hello")

        irc_session.get_reply(client1, expect_timeout = True)
        
        
@pytest.mark.category("CHANNEL_PART")
class TestPART(object):
    def _test_join_and_part(self, irc_session, numclients):
        """
        Connect `numclients` clients to the server, have them all
        join channel #test and then have them all leave channel #test
        """
        clients = irc_session.connect_clients(numclients, join_channel = "#test")
        irc_session.part_channel(clients, "#test")
        
    def _test_join_and_part_and_join_and_part(self, irc_session, numclients):
        """
        Connect `numclients` clients to the server, have them all
        join channel #test and then have them all leave channel #test,
        and then have them join and leave again.
        """
        clients = irc_session.connect_clients(numclients, join_channel = "#test")
        irc_session.part_channel(clients, "#test")        
        irc_session.join_channel(clients, "#test")
        irc_session.part_channel(clients, "#test")


    def test_channel_part1(self, irc_session):
        """
        Two clients connect to the server and join #test. The first
        user leaves #test. Both clients should get a relay of the PART
        message.
        """
        clients = irc_session.connect_clients(2, join_channel = "#test")
        
        nick1, client1 = clients[0]
        nick2, client2 = clients[1]
        
        client1.send_cmd("PART #test")
        irc_session.verify_relayed_part(client1, from_nick=nick1, channel="#test", msg=None)
        irc_session.verify_relayed_part(client2, from_nick=nick1, channel="#test", msg=None)


    def test_channel_part2(self, irc_session):
        """
        Two clients connect to the server and join #test. The first
        user leaves #test (with a custom message). Both clients should 
        get a relay of the PART message.
        """
        clients = irc_session.connect_clients(2, join_channel = "#test")
        
        nick1, client1 = clients[0]
        nick2, client2 = clients[1]
        
        client1.send_cmd("PART #test :I'm out of here!")
        irc_session.verify_relayed_part(client1, from_nick=nick1, channel="#test", msg="I'm out of here!")
        irc_session.verify_relayed_part(client2, from_nick=nick1, channel="#test", msg="I'm out of here!")
                

    def test_channel_part3(self, irc_session):
        """
        Two clients connect to the server and join #test.
        
        The first one sends a PRIVMSG to the channel. Then, the second one
        leaves the channel. The first one sends another PRIVMSG to the channel.
        The second one shouldn't receive anything.
        """
        
        clients = irc_session.connect_clients(2, join_channel = "#test")
        
        nick1, client1 = clients[0]
        nick2, client2 = clients[1]
        
        client1.send_cmd("PRIVMSG #test :Hello!")
        irc_session.verify_relayed_privmsg(client2, from_nick=nick1, recip="#test", msg="Hello!")
        
        client2.send_cmd("PART #test")
        irc_session.verify_relayed_part(client2, from_nick=nick2, channel="#test", msg=None)          
        irc_session.verify_relayed_part(client1, from_nick=nick2, channel="#test", msg=None)
        
        client1.send_cmd("PRIVMSG #test :Hello?")
        irc_session.get_reply(client2, expect_timeout = True)
                        

    def test_channel_part4(self, irc_session):
        """
        Two clients connect to the server, join a channel, and then leave it.
        """
        self._test_join_and_part(irc_session, 2)
        

    def test_channel_part5(self, irc_session):
        """
        Five clients connect to the server, join a channel, and then leave it.
        """
        self._test_join_and_part(irc_session, 5)


    def test_channel_part6(self, irc_session):
        """
        Twenty clients connect to the server, join a channel, and then leave it.
        """
        self._test_join_and_part(irc_session, 20)         
        

    def test_channel_part7(self, irc_session):
        """
        Two clients connect to the server, join a channel, then leave it,
        then join it again, and leave it again.
        """        
        self._test_join_and_part_and_join_and_part(irc_session, 2)


    def test_channel_part8(self, irc_session):
        """
        Five clients connect to the server, join a channel, then leave it,
        then join it again, and leave it again.
        """        
        self._test_join_and_part_and_join_and_part(irc_session, 5)


    def test_channel_part9(self, irc_session):
        """
        Twenty clients connect to the server, join a channel, then leave it,
        then join it again, and leave it again.
        """        
        self._test_join_and_part_and_join_and_part(irc_session, 10)


    def test_channel_part_nochannel1(self, irc_session):
        """
        A client connects to the server and tries to leave a channel
        the user is not in (furthermore, the channel doesn't exist)
        """
        
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("PART #test")

        reply = irc_session.get_reply(client1, expect_code = replies.ERR_NOSUCHCHANNEL, expect_nick = "user1", 
                               expect_nparams = 2, expect_short_params = ["#test"],
                               long_param_re = "No such channel")      
        

    def test_channel_part_nochannel2(self, irc_session):
        """
        A client connects to the server, joins the #test channel
        and leaves it. Then, the user tries to leave a channel
        again.
        """
        
        clients = irc_session.connect_clients(1, join_channel = "#test")
        irc_session.part_channel(clients, "#test")  
        
        nick1, client1 = clients[0]
      
        client1.send_cmd("PART #test")

        reply = irc_session.get_reply(client1, expect_code = replies.ERR_NOSUCHCHANNEL, expect_nick = nick1, 
                               expect_nparams = 2, expect_short_params = ["#test"],
                               long_param_re = "No such channel")              
        

    def test_channel_part_notonchannel1(self, irc_session):
        """
        Two clients connect to the server. The first one joins #test,
        and the second one tries to leave #test (the second client
        is not in the channel, but the channel exists)
        """
        client1 = irc_session.connect_user("user1", "User One")
        client2 = irc_session.connect_user("user2", "User Two")
        
        client1.send_cmd("JOIN #test")   
        irc_session.verify_join(client1, "user1", "#test")
          
        client2.send_cmd("PART #test")
            
        reply = irc_session.get_reply(client2, expect_code = replies.ERR_NOTONCHANNEL, expect_nick = "user2", 
                               expect_nparams = 2, expect_short_params = ["#test"],
                               long_param_re = "You're not on that channel")          
        

    def test_channel_part_notonchannel2(self, irc_session):
        """
        Two clients connect to the server and both join #test.
        The first one leaves the channel, and then tries to leave
        again.
        """
        clients = irc_session.connect_clients(2, join_channel = "#test") 
        
        nick1, client1 = clients[0]
        client1.send_cmd("PART #test")
        irc_session.verify_relayed_part(client1, from_nick=nick1, channel="#test", msg=None)    

        client1.send_cmd("PART #test")
        reply = irc_session.get_reply(client1, expect_code = replies.ERR_NOTONCHANNEL, expect_nick = nick1, 
                               expect_nparams = 2, expect_short_params = ["#test"],
                               long_param_re = "You're not on that channel")

    def test_channel_part_params(self, irc_session):
        """
        Test ERR_NEEDMOREPARAMS reply
        """
        
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("PART")
        
        irc_session.get_ERR_NEEDMOREPARAMS_reply(client1, 
                                                 expect_nick="user1", expect_cmd="PART")

        
@pytest.mark.category("CHANNEL_TOPIC")        
class TestTOPIC(object):

    def test_topic01(self, irc_session):
        """
        A client connects to the server, joins #test and sets the channel topic
        """
        
        topic = "This is the channel's topic"
        
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        
        irc_session.verify_join(client1, "user1", "#test")    
        
        client1.send_cmd("TOPIC #test :%s" % topic)
        
        irc_session.verify_relayed_topic(client1, from_nick="user1", channel="#test", topic=topic)


    def test_topic02(self, irc_session):
        """
        A client connects to the server, joins #test, sets the channel topic,
        and then asks for the topic.
        """
        
        topic = "This is the channel's topic"
        
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        
        irc_session.verify_join(client1, "user1", "#test")    
        
        client1.send_cmd("TOPIC #test :%s" % topic)
        
        irc_session.verify_relayed_topic(client1, from_nick="user1", channel="#test", topic=topic)
        
        client1.send_cmd("TOPIC #test")
        
        reply = irc_session.get_reply(client1, expect_code = replies.RPL_TOPIC, expect_nick = "user1", 
                               expect_nparams = 2, expect_short_params = ["#test"],
                               long_param_re = topic)        


    def test_topic03(self, irc_session):
        """
        A client connects to the server, joins #test and then asks for the topic
        (but no topic has been set)
        """
        
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        
        irc_session.verify_join(client1, "user1", "#test")    
        
        client1.send_cmd("TOPIC #test")
        
        reply = irc_session.get_reply(client1, expect_code = replies.RPL_NOTOPIC, expect_nick = "user1", 
                               expect_nparams = 2, expect_short_params = ["#test"],
                               long_param_re = "No topic is set")        
        

    def test_topic04(self, irc_session):
        """
        A client connects to the server and asks for the topic of a channel
        that does not exists.
        """
        
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("TOPIC #test")
        
        reply = irc_session.get_reply(client1, expect_code = replies.ERR_NOTONCHANNEL, expect_nick = "user1", 
                               expect_nparams = 2, expect_short_params = ["#test"],
                               long_param_re = "You're not on that channel")             
    

    def test_topic05(self, irc_session):
        """
        A client connects to the server and tries to set the topic of a channel
        that does not exists.
        """        
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("TOPIC #test :This is the channel's topic")
        
        reply = irc_session.get_reply(client1, expect_code = replies.ERR_NOTONCHANNEL, expect_nick = "user1", 
                               expect_nparams = 2, expect_short_params = ["#test"],
                               long_param_re = "You're not on that channel")       
        

    def test_topic06(self, irc_session):
        """
        Two clients connect to the server. The first one joins #test, the
        second one does not. The second one tries to ask for the channel topic.
        """
                
        client1 = irc_session.connect_user("user1", "User One")
        client2 = irc_session.connect_user("user2", "User Two")
        
        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, "user1", "#test")    
        
        client2.send_cmd("TOPIC #test")
        reply = irc_session.get_reply(client2, expect_code = replies.ERR_NOTONCHANNEL, expect_nick = "user2", 
                               expect_nparams = 2, expect_short_params = ["#test"],
                               long_param_re = "You're not on that channel")       


    def test_topic07(self, irc_session):
        """
        Two clients connect to the server. The first one joins #test and sets
        the channel topic. The second one does not join the channel, but
        tries to ask for the channel topic.
        """        
        client1 = irc_session.connect_user("user1", "User One")
        client2 = irc_session.connect_user("user2", "User Two")
       
        topic = "This is the channel's topic"
        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, "user1", "#test")    
        client1.send_cmd("TOPIC #test :%s" % topic)
        irc_session.verify_relayed_topic(client1, from_nick="user1", channel="#test", topic=topic)
        
        client2.send_cmd("TOPIC #test")
        reply = irc_session.get_reply(client2, expect_code = replies.ERR_NOTONCHANNEL, expect_nick = "user2", 
                               expect_nparams = 2, expect_short_params = ["#test"],
                               long_param_re = "You're not on that channel")       
  

    def test_topic08(self, irc_session):
        """
        Two clients connect to the server. The first one joins #test and sets
        the channel topic. The second one joins after that, and should receive
        the topic when joining.
        """               
        client1 = irc_session.connect_user("user1", "User One")
        client2 = irc_session.connect_user("user2", "User Two")
       
        topic = "This is the channel's topic"
        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, "user1", "#test")    
        client1.send_cmd("TOPIC #test :%s" % topic)
        irc_session.verify_relayed_topic(client1, from_nick="user1", channel="#test", topic=topic)

        client2.send_cmd("JOIN #test")
        irc_session.verify_join(client2, "user2", "#test", expect_topic=topic)    
        

    def test_topic09(self, irc_session):
        """
        Ten clients connect to the server and join #test. The first
        user changes the topic of the channel. Everyone should
        receive the relay of the topic.
        """
        
        clients = irc_session.connect_clients(10, join_channel = "#test")
        
        nick1, client1 = clients[0]
        
        topic = "This is the channel's topic"
        client1.send_cmd("TOPIC #test :%s" % topic)
                
        for nick, client in clients:
            irc_session.verify_relayed_topic(client, from_nick=nick1, channel="#test", topic=topic)    
            

    def test_topic10(self, irc_session):
        """
        Ten clients connect to the server. The first one joins #test
        and sets the channel topic. The remaining nine then join
        the channel, and should all receive the topic when joining
        """
        clients = irc_session.connect_clients(10)
        
        nick1, client1 = clients[0]
        
        topic = "This is the channel's topic"
        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, "user1", "#test")    
        client1.send_cmd("TOPIC #test :%s" % topic)
        irc_session.verify_relayed_topic(client1, from_nick="user1", channel="#test", topic=topic)
        
        for nick, client in clients[1:]:
            client.send_cmd("JOIN #test")
            irc_session.verify_join(client, nick, "#test", expect_topic=topic)
            
            
    def test_topic_params(self, irc_session):
        """
        Test ERR_NEEDMOREPARAMS reply
        """
        
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("TOPIC")
        
        irc_session.get_ERR_NEEDMOREPARAMS_reply(client1, 
                                                 expect_nick="user1", expect_cmd="TOPIC")            
        
        
@pytest.mark.category("NAMES")                
class TestNAMES(object):
    
    def _test_names_channel(self, irc_session, channels, client, nick):
        """
        `channels` is a dictionary mapping channels to the users
        in that channel. Send the NAMES command for each channel,
        and verify that the replies are correct.
        """
        channelsl = [k for k in channels.keys() if k is not None]
        channelsl.sort()
        for channel in channelsl:
            channelusers = channels[channel]
            client.send_cmd("NAMES %s" % channel)
            irc_session.verify_names(client, nick, expect_channel = channel, expect_names = channelusers)
            
    def _test_names_all(self, irc_session, channels, client, nick):
        """
        `channels` is a dictionary mapping channels to the users
        in that channel. Send the NAMES command without a parameter,
        and verify the replies.
        """        
        client.send_cmd("NAMES")

        channelsl = set([k for k in channels.keys() if k is not None])
        numchannels = len(channelsl)
        
        for i in range(numchannels):
            reply = irc_session.get_reply(client, expect_code = replies.RPL_NAMREPLY, expect_nick = nick,
                                          expect_nparams = 3)    
            channel = reply.params[2]
            assert channel in channelsl, "Received unexpected RPL_NAMREPLY for {}: {}".format(channel, reply._s)    
            irc_session.verify_names_single(reply, nick, expect_channel = channel, expect_names = channels[channel])
            channelsl.remove(channel)
            
        assert len(channelsl) == 0, "Did not receive RPL_NAMREPLY for these channels: {}".format(", ".join(channelsl))
                
        if None not in channels:
            no_channel = []
        else:
            no_channel = channels[None]

        if len(no_channel) > 0:
            irc_session.verify_names(client, nick, expect_channel = "*", expect_names = no_channel)
        else:
            irc_session.get_reply(client, expect_code = replies.RPL_ENDOFNAMES, expect_nick = nick,
                                  expect_nparams = 2)    
     


    def test_names1(self, irc_session):
        """
        Connects nine users to the server, and has them join
        the following channels, and set the following privileges:
        (@ denotes channel operators):
        
        #test1: @user1, user2, user3
        #test2: @user4, user5, user6
        #test3: @user7, user8, user9
        
        This test verifies that the correct RPL_NAMREPLY and RPL_ENDOFNAMES
        replies are sent when each of the users joins a channel.
        """        
        irc_session.connect_and_join_channels(channels1, test_names = True)
        

    def test_names2(self, irc_session):
        """
        Connects eleven users to the server, and has them join
        the following channels, and set the following privileges:
        (@ denotes channel operators):
        
        #test1: @user1, user2, user3
        #test2: @user4, user5, user6
        #test3: @user7, user8, user9
        
        Not in a channel: user10, user11  
        
        This test verifies that the correct RPL_NAMREPLY and RPL_ENDOFNAMES
        replies are sent when each of the users joins a channel.
        """        
        irc_session.connect_and_join_channels(channels2, test_names = True)


    def test_names3(self, irc_session):
        """
        Connects eleven users to the server, and has them join
        the following channels, and set the following privileges:
        (@ denotes channel operators, and + denotes a user with voice privileges):
        
        #test1: @user1, user2, user3
        #test2: @user2
        #test3: @user3, @user4, user5, user6
        #test4: @user7, +user8, +user9, user1, user2
        #test5: @user1, @user5 
        
        Not in a channel: user10, user11    
        
        This test verifies that the correct RPL_NAMREPLY and RPL_ENDOFNAMES
        replies are sent when each of the users joins a channel.       
        """      
        irc_session.connect_and_join_channels(channels3, test_names = True)     
        


    def test_names4(self, irc_session):
        """
        Connects nine users to the server, and has them join
        the following channels, and set the following privileges:
        (@ denotes channel operators):
        
        #test1: @user1, user2, user3
        #test2: @user4, user5, user6
        #test3: @user7, user8, user9
        
        This test send a NAMES command for each of the channels and verifies
        the replies.
        """        
        users = irc_session.connect_and_join_channels(channels1, test_names = True)
        
        self._test_names_channel(irc_session, channels1, users["user1"], "user1")
        

    def test_names5(self, irc_session):
        """
        Connects eleven users to the server, and has them join
        the following channels, and set the following privileges:
        (@ denotes channel operators):
        
        #test1: @user1, user2, user3
        #test2: @user4, user5, user6
        #test3: @user7, user8, user9
        
        Not in a channel: user10, user11  
        
        This test send a NAMES command for each of the channels and verifies
        the replies.
        """        
        users = irc_session.connect_and_join_channels(channels2, test_names = True)
        
        self._test_names_channel(irc_session, channels2, users["user1"], "user1")


    def test_names6(self, irc_session):
        """
        Connects eleven users to the server, and has them join
        the following channels, and set the following privileges:
        (@ denotes channel operators, and + denotes a user with voice privileges):
        
        #test1: @user1, user2, user3
        #test2: @user2
        #test3: @user3, @user4, user5, user6
        #test4: @user7, +user8, +user9, user1, user2
        #test5: @user1, @user5 
        
        Not in a channel: user10, user11    
        
        This test send a NAMES command for each of the channels and verifies
        the replies.
        """      
        users = irc_session.connect_and_join_channels(channels3, test_names = True)
        
        self._test_names_channel(irc_session, channels3, users["user1"], "user1")
        
        

    def test_names7(self, irc_session):
        """
        Connects nine users to the server, and has them join
        the following channels, and set the following privileges:
        (@ denotes channel operators):
        
        #test1: @user1, user2, user3
        #test2: @user4, user5, user6
        #test3: @user7, user8, user9
        
        This test send a NAMES command without a parameter and verifies
        the replies.
        """        
        users = irc_session.connect_and_join_channels(channels1, test_names = True)
        
        self._test_names_all(irc_session, channels1, users["user1"], "user1")
        

    def test_names8(self, irc_session):
        """
        Connects eleven users to the server, and has them join
        the following channels, and set the following privileges:
        (@ denotes channel operators):
        
        #test1: @user1, user2, user3
        #test2: @user4, user5, user6
        #test3: @user7, user8, user9
        
        Not in a channel: user10, user11  
        
        This test send a NAMES command without a parameter and verifies
        the replies.
        """        
        users = irc_session.connect_and_join_channels(channels2, test_names = True)
        
        self._test_names_all(irc_session, channels2, users["user1"], "user1")


    def test_names9(self, irc_session):
        """
        Connects eleven users to the server, and has them join
        the following channels, and set the following privileges:
        (@ denotes channel operators, and + denotes a user with voice privileges):
        
        #test1: @user1, user2, user3
        #test2: @user2
        #test3: @user3, @user4, user5, user6
        #test4: @user7, +user8, +user9, user1, user2
        #test5: @user1, @user5 
        
        Not in a channel: user10, user11    
        
        This test send a NAMES command without a parameter and verifies
        the replies.
        """      
        users = irc_session.connect_and_join_channels(channels3, test_names = True)                    
        
        self._test_names_all(irc_session, channels3, users["user1"], "user1")
        

    def test_names10(self, irc_session):
        """
        Connects five users to the server, with none of them joining any channels.    
        
        This test send a NAMES command without a parameter and verifies
        the replies.
        """      
        users = irc_session.connect_and_join_channels(channels4, test_names = True)                    
        
        self._test_names_all(irc_session, channels4, users["user1"], "user1")        
        
        

    def test_names11(self, irc_session):
        """
        Connects nine users to the server, and has them join
        the following channels, and set the following privileges:
        (@ denotes channel operators):
        
        #test1: @user1, user2, user3
        #test2: @user4, user5, user6
        #test3: @user7, user8, user9
        
        user1 then sends a NAMES command for a channel that does not
        exist
        """
        
        users = irc_session.connect_and_join_channels(channels1, test_names = True)
        
        users["user1"].send_cmd("NAMES #noexist")
        irc_session.get_reply(users["user1"], expect_code = replies.RPL_ENDOFNAMES, expect_nick = "user1",
                   expect_nparams = 2)                


@pytest.mark.category("LIST")                
class TestLIST(object):
            
    def _test_list(self, irc_session, channels, client, nick, expect_topics = None):
        """
        User `nick` sends a LIST command and we verify the replies.
        `channels` is a dictionary mapping channel names to users in each channel.
        `expect_topics` is a dictionary mapping channel names to their topics
        """
        
        client.send_cmd("LIST")

        channelsl = set([k for k in channels.keys() if k is not None])
        numchannels = len(channelsl)
        
        for i in range(numchannels):
            reply = irc_session.get_reply(client, expect_code = replies.RPL_LIST, expect_nick = nick,
                           expect_nparams = 3)    

            channel = reply.params[1]
            irc_session._assert_in(channel, channelsl, 
                                   explanation = "Received unexpected RPL_LIST for {}".format(channel),
                                   irc_msg = reply)            
            
            numusers = int(reply.params[2])
            expect_numusers = len(channels[channel])
            irc_session._assert_equals(numusers, expect_numusers, 
                                       explanation = "Expected {} users in {}, got {}".format(expect_numusers, channel, numusers),
                                       irc_msg = reply)            
                        
            if expect_topics is not None:
                expect_topic = expect_topics[channel]
                topic = reply.params[3][1:]
                irc_session._assert_equals(topic, expect_topic, 
                                           explanation = "Expected topic for {} to be '{}', got '{}' instead".format(channel, expect_topic, topic),
                                           irc_msg = reply)    
                
            channelsl.remove(channel)
            
        assert len(channelsl) == 0, "Did not receive RPL_LIST for these channels: {}".format(", ".join(channelsl))
                
        irc_session.get_reply(client, expect_code = replies.RPL_LISTEND, expect_nick = nick,
                       expect_nparams = 1, long_param_re = "End of LIST")    
        


    def test_list1(self, irc_session):
        """
        Connects nine users to the server, and has them join
        the following channels, and set the following privileges:
        (@ denotes channel operators):
        
        #test1: @user1, user2, user3
        #test2: @user4, user5, user6
        #test3: @user7, user8, user9
        
        user1 then sends a LIST command.
        """        
        users = irc_session.connect_and_join_channels(channels1)
        
        self._test_list(irc_session, channels1, users["user1"], "user1")
        

    def test_list2(self, irc_session):
        """
        Connects eleven users to the server, and has them join
        the following channels, and set the following privileges:
        (@ denotes channel operators):
        
        #test1: @user1, user2, user3
        #test2: @user4, user5, user6
        #test3: @user7, user8, user9
        
        Not in a channel: user10, user11  
        
        user1 then sends a LIST command.
        """        
        users = irc_session.connect_and_join_channels(channels2)
        
        self._test_list(irc_session, channels2, users["user1"], "user1")
        

    def test_list3(self, irc_session):
        """
        Connects eleven users to the server, and has them join
        the following channels, and set the following privileges:
        (@ denotes channel operators, and + denotes a user with voice privileges):
        
        #test1: @user1, user2, user3
        #test2: @user2
        #test3: @user3, @user4, user5, user6
        #test4: @user7, +user8, +user9, user1, user2
        #test5: @user1, @user5 
        
        Not in a channel: user10, user11    
        
        user1 then sends a LIST command.
        """      
        users = irc_session.connect_and_join_channels(channels3)
        
        self._test_list(irc_session, channels3, users["user1"], "user1")
        

    def test_list4(self, irc_session):
        """
        Connects five users to the server, with none of them joining any channels.    
        
        user1 then sends a LIST command.
        """      
        users = irc_session.connect_and_join_channels(channels4)
        
        self._test_list(irc_session, channels4, users["user1"], "user1")        
        
  

    def test_list5(self, irc_session):
        """
        Connects eleven users to the server, and has them join
        the following channels, and set the following privileges:
        (@ denotes channel operators):
        
        #test1: @user1, user2, user3
        #test2: @user4, user5, user6
        #test3: @user7, user8, user9
        
        Not in a channel: user10, user11  
        
        The operator in each channel then sets the topic for the
        channel. user10 sends a LIST command, and the replies
        should include the topics of the channels.
        """                
        users = irc_session.connect_and_join_channels(channels2)
        
        users["user1"].send_cmd("TOPIC #test1 :Topic One")
        irc_session.verify_relayed_topic(users["user1"], from_nick="user1", channel="#test1", topic="Topic One")
        
        users["user4"].send_cmd("TOPIC #test2 :Topic Two")
        irc_session.verify_relayed_topic(users["user4"], from_nick="user4", channel="#test2", topic="Topic Two")

        users["user7"].send_cmd("TOPIC #test3 :Topic Three")
        irc_session.verify_relayed_topic(users["user7"], from_nick="user7", channel="#test3", topic="Topic Three")

        self._test_list(irc_session, channels2, users["user10"], "user10",
                        expect_topics = {"#test1": "Topic One",
                                         "#test2": "Topic Two",
                                         "#test3": "Topic Three"})      
        
@pytest.mark.category("WHO")                        
class TestWHO(object):
            
    def _test_who(self, irc_session, channels, client, nick, channel, aways = None, ircops = None):
        """
        User `nick` sends a WHO command with `channel` as a parameter, and
        we verify that the replies are correct.
        
        `channels` is a dictionary mapping channel names to users in each channel.
        `aways` is a list of users that are away, and `ircops` is a list of users
        that are IRCops.
        """
        
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
            reply = irc_session.get_reply(client, expect_code = replies.RPL_WHOREPLY, expect_nick = nick,
                                          expect_nparams = 7, expect_short_params = [channel])
            
            ircop = False
            away = False
            who_nick = reply.params[5]
            status = reply.params[6]
            
            irc_session._assert_in(len(status), (1,2,3), 
                                   explanation = "Invalid status string '{}'".format(status),
                                   irc_msg = reply)    

            irc_session._assert_in(status[0], ('H','G'), 
                                   explanation = "Invalid status string '{}'".format(status),
                                   irc_msg = reply)
            
            if status[0] == 'G':
                away = True

            if len(status) == 1:
                qwho_nick = who_nick
            if len(status) == 2:
                if status[1] == '*':
                    ircop = True
                    qwho_nick = who_nick
                else:
                    irc_session._assert_in(status[1], ('@','+'), 
                                           explanation = "Invalid status string '{}'".format(status),
                                           irc_msg = reply)
                    qwho_nick = status[1] + who_nick
            elif len(status) == 3:
                irc_session._assert_equals(status[1], ('*'), 
                                           explanation = "Invalid status string '{}'".format(status),
                                           irc_msg = reply)
                irc_session._assert_in(status[2], ('@','+'), 
                                       explanation = "Invalid status string '{}'".format(status),
                                       irc_msg = reply)
                ircop = True
                qwho_nick = status[2] + who_nick
            
            irc_session._assert_in(qwho_nick, users, 
                                   explanation = "Received unexpected RPL_WHOREPLY for {}".format(who_nick),
                                   irc_msg = reply)               
            
            if ircops is not None:
                if who_nick in ircops:
                    irc_session._assert_equals(ircop, True, 
                                               explanation = "Expected {} to be an IRCop".format(who_nick),
                                               irc_msg = reply)
                else:    
                    irc_session._assert_equals(ircop, False, 
                                               explanation = "Did not expect {} to be an IRCop".format(who_nick),
                                               irc_msg = reply)
            
            if aways is not None:
                if who_nick in aways:
                    irc_session._assert_equals(away, True, 
                                               explanation = "Expected {} to be away".format(who_nick),
                                               irc_msg = reply)
                else:    
                    irc_session._assert_equals(away, False, 
                                               explanation = "Did not expect {} to be away".format(who_nick),
                                               irc_msg = reply)
                
            users.remove(qwho_nick)
            
        assert len(users) == 0, "Did not receive RPL_WHOREPLY for these users: {}".format(", ".join(users))
                
        irc_session.get_reply(client, expect_code = replies.RPL_ENDOFWHO, expect_nick = nick,
                       expect_nparams = 2, expect_short_params = [channel],
                       long_param_re = "End of WHO list")    
        


    def test_who1(self, irc_session):
        """
        Connects nine users to the server, and has them join
        the following channels, and set the following privileges:
        (@ denotes channel operators):
        
        #test1: @user1, user2, user3
        #test2: @user4, user5, user6
        #test3: @user7, user8, user9
        
        user1 then sends a WHO for each channel.
        """               
        users = irc_session.connect_and_join_channels(channels1)
        
        self._test_who(irc_session, channels1, users["user1"], "user1", channel = "#test1")        
        self._test_who(irc_session, channels1, users["user1"], "user1", channel = "#test2")        
        self._test_who(irc_session, channels1, users["user1"], "user1", channel = "#test3")
        

    def test_who2(self, irc_session):
        """
        Connects nine users to the server, and has them join
        the following channels, and set the following privileges:
        (@ denotes channel operators):
        
        #test1: @user1, user2, user3
        #test2: @user4, user5, user6
        #test3: @user7, user8, user9
        
        user1, user4, and user7 each send a "WHO *" command.
        """               
        users = irc_session.connect_and_join_channels(channels1)
        
        self._test_who(irc_session, channels1, users["user1"], "user1", channel = "*")        
        self._test_who(irc_session, channels1, users["user4"], "user4", channel = "*")        
        self._test_who(irc_session, channels1, users["user7"], "user7", channel = "*")        
        

    def test_who3(self, irc_session):
        """
        Connects eleven users to the server, and has them join
        the following channels, and set the following privileges:
        (@ denotes channel operators):
        
        #test1: @user1, user2, user3
        #test2: @user4, user5, user6
        #test3: @user7, user8, user9
        
        Not in a channel: user10, user11  
        
        user1, user4, user7, and user10 each send a "WHO *" command.
        """               
        users = irc_session.connect_and_join_channels(channels2)
        
        self._test_who(irc_session, channels2, users["user1"], "user1", channel = "*")        
        self._test_who(irc_session, channels2, users["user4"], "user4", channel = "*")        
        self._test_who(irc_session, channels2, users["user7"], "user7", channel = "*")             
        self._test_who(irc_session, channels2, users["user10"], "user10", channel = "*")             
        

    def test_who4(self, irc_session):
        """
        Connects eleven users to the server, and has them join
        the following channels, and set the following privileges:
        (@ denotes channel operators, and + denotes a user with voice privileges):
        
        #test1: @user1, user2, user3
        #test2: @user2
        #test3: @user3, @user4, user5, user6
        #test4: @user7, +user8, +user9, user1, user2
        #test5: @user1, @user5 
        
        Not in a channel: user10, user11    
        
        user1 then sends a WHO for each channel.
        """          
        users = irc_session.connect_and_join_channels(channels3)
        
        self._test_who(irc_session, channels3, users["user1"], "user1", channel = "#test1")        
        self._test_who(irc_session, channels3, users["user1"], "user1", channel = "#test2")        
        self._test_who(irc_session, channels3, users["user1"], "user1", channel = "#test3")                     
        self._test_who(irc_session, channels3, users["user1"], "user1", channel = "#test4")        
        self._test_who(irc_session, channels3, users["user1"], "user1", channel = "#test5")       
        
        

    def test_who5(self, irc_session):
        """
        Connects nine users to the server, and has them join
        the following channels, and set the following privileges:
        (@ denotes channel operators):
        
        #test1: @user1, user2, user3
        #test2: @user4, user5, user6
        #test3: @user7, user8, user9
        
        user4, user5, and user7 mark themselves as away. user4 and user6 become
        IRCops. user1 then sends a WHO for each channel.
        """                  
        aways = ["user4", "user5", "user7"]
        ircops = ["user4", "user6"]

        users = irc_session.connect_and_join_channels(channels1, aways, ircops)
                
        self._test_who(irc_session, channels1, users["user1"], "user1", channel = "#test1", aways = aways, ircops = ircops)        
        self._test_who(irc_session, channels1, users["user1"], "user1", channel = "#test2", aways = aways, ircops = ircops)        
        self._test_who(irc_session, channels1, users["user1"], "user1", channel = "#test3", aways = aways, ircops = ircops)     
        
        

    def test_who6(self, irc_session):
        """
        Connects eleven users to the server, and has them join
        the following channels, and set the following privileges:
        (@ denotes channel operators, and + denotes a user with voice privileges):
        
        #test1: @user1, user2, user3
        #test2: @user2
        #test3: @user3, @user4, user5, user6
        #test4: @user7, +user8, +user9, user1, user2
        #test5: @user1, @user5 
        
        Not in a channel: user10, user11    
        
        user4, user8, and user10 mark themselves as away. user8, user9, user10,
        and user11 become IRCops. user1 then sends a WHO for each channel.
        """              
        aways = ["user4", "user8", "user10"]
        ircops = ["user8", "user9", "user10", "user11"]
        
        users = irc_session.connect_and_join_channels(channels3, aways, ircops)     
        
        self._test_who(irc_session, channels3, users["user1"], "user1", channel = "#test1", aways = aways, ircops = ircops)        
        self._test_who(irc_session, channels3, users["user1"], "user1", channel = "#test2", aways = aways, ircops = ircops)        
        self._test_who(irc_session, channels3, users["user1"], "user1", channel = "#test3", aways = aways, ircops = ircops)                     
        self._test_who(irc_session, channels3, users["user1"], "user1", channel = "#test4", aways = aways, ircops = ircops)        
        self._test_who(irc_session, channels3, users["user1"], "user1", channel = "#test5", aways = aways, ircops = ircops)                            
                 
                 
@pytest.mark.category("UPDATE_ASSIGNMENT2")                                 
class TestChannelUPDATEAssignment2(object):

    def test_update1b_nick(self, irc_session):
        """
        Ensure that nick changes are relayed in a channel.
        """
        clients = irc_session.connect_clients(5, join_channel = "#test")
        
        nick1, client1 = clients[0]
        
        client1.send_cmd("NICK userfoo")
                
        for nick, client in clients:
            irc_session.verify_relayed_nick(client, from_nick=nick1, newnick="userfoo")         
            

    def test_update1b_quit1(self, irc_session):
        """
        Ensure that a user's QUIT is relayed to the channels the user is in.
        """
        clients = irc_session.connect_clients(5, join_channel = "#test")
        
        nick1, client1 = clients[0]
        
        client1.send_cmd("QUIT")
                
        for nick, client in clients[1:]:
            irc_session.verify_relayed_quit(client, from_nick=nick1, msg = "Client Quit")           
            
        irc_session.get_message(client1, expect_cmd = "ERROR", expect_nparams = 1,
                                long_param_re = "Closing Link: .* \(Client Quit\)")               
            
        irc_session.verify_disconnect(client1)


    def test_update1b_quit2(self, irc_session):
        """
        Ensure that a user's QUIT (with a custom message) is relayed to the 
        channels the user is in.
        """        
        clients = irc_session.connect_clients(5, join_channel = "#test")
        
        nick1, client1 = clients[0]
        
        client1.send_cmd("QUIT :I'm outta here")
                
        for nick, client in clients[1:]:
            irc_session.verify_relayed_quit(client, from_nick=nick1, msg = "I'm outta here")   
            
        irc_session.get_message(client1, expect_cmd = "ERROR", expect_nparams = 1,
                                long_param_re = "Closing Link: .* \(I'm outta here\)")   
                    
        irc_session.verify_disconnect(client1)
                                                                                                      
import time
import pytest
from chirc.tests.fixtures import channels1, channels2, channels3
from chirc import replies

@pytest.mark.category("LUSERS")
class TestConnectionWithLUSERSMOTD(object):

    def test_connect_lusers_motd1(self, irc_session):
        """
        Test correct values in LUSERS with one client connected
        """
        
        client = irc_session.get_client()
        
        client.send_cmd("NICK user1")
        client.send_cmd("USER user1 * * :User One")
        
        irc_session.verify_welcome_messages(client, "user1")
        irc_session.verify_lusers(client, "user1", 
                                  expect_users = 1, 
                                  expect_ops = 0, 
                                  expect_unknown = 0, 
                                  expect_channels = 0, 
                                  expect_clients = 1)

        irc_session.verify_motd(client, "user1")         
        
    def test_connect_lusers_motd2(self, irc_session):
        """
        Test correct values in LUSERS with one client connected
        (connecting by sending USER first instead of NICK)
        """
        
        client = irc_session.get_client()
        
        client.send_cmd("USER user1 * * :User One")
        client.send_cmd("NICK user1")
        
        irc_session.verify_welcome_messages(client, "user1")
        irc_session.verify_lusers(client, "user1", 
                                  expect_users = 1, 
                                  expect_ops = 0, 
                                  expect_unknown = 0, 
                                  expect_channels = 0, 
                                  expect_clients = 1)

        irc_session.verify_motd(client, "user1")         
        

    def test_connect_lusers_motd_2users(self, irc_session):
        """
        Test correct values in LUSERS with two clients connected
        """
                
        client1 = irc_session.get_client()
        
        client1.send_cmd("NICK user1")
        client1.send_cmd("USER user1 * * :User One")

        irc_session.verify_welcome_messages(client1, "user1")
        irc_session.verify_lusers(client1, "user1", 
                                  expect_users = 1, 
                                  expect_ops = 0, 
                                  expect_unknown = 0, 
                                  expect_channels = 0, 
                                  expect_clients = 1)
        irc_session.verify_motd(client1, "user1")         


        client2 = irc_session.get_client()
        client2.send_cmd("NICK user2")
        client2.send_cmd("USER user2 * * :User Two")
        
        irc_session.verify_welcome_messages(client2, "user2")
        irc_session.verify_lusers(client2, "user2", 
                                  expect_users = 2, 
                                  expect_ops = 0, 
                                  expect_unknown = 0, 
                                  expect_channels = 0, 
                                  expect_clients = 2)
        irc_session.verify_motd(client2, "user2")         

    def test_connect_lusers_motd_unknown(self, irc_session):
        """
        Test correct values in LUSERS with two clients connected,
        one of which is "unknown" (hasn't completed its registration)
        """
                
        unknown1 = irc_session.get_client()
        time.sleep(0.05)
        
        client1 = irc_session.get_client()
        client1.send_cmd("NICK user1")
        client1.send_cmd("USER user1 * * :User One")

        time.sleep(0.05)

        irc_session.verify_welcome_messages(client1, "user1")
        irc_session.verify_lusers(client1, "user1", 
                                  expect_users = 1, 
                                  expect_ops = 0, 
                                  expect_unknown = 1, 
                                  expect_channels = 0, 
                                  expect_clients = 2)
        irc_session.verify_motd(client1, "user1")       
        
    def test_connect_lusers_motd_unknown2(self, irc_session):
        """
        Test correct values in LUSERS with two clients connected,
        one of which is "unknown" (hasn't completed its registration,
        but has sent a NICK command)
        """        
        unknown1 = irc_session.get_client()
        unknown1.send_cmd("NICK unknown1")
        time.sleep(0.05)
        
        client1 = irc_session.get_client()
        client1.send_cmd("NICK user1")
        client1.send_cmd("USER user1 * * :User One")

        irc_session.verify_welcome_messages(client1, "user1")
        irc_session.verify_lusers(client1, "user1", 
                                  expect_users = 1, 
                                  expect_ops = 0, 
                                  expect_unknown = 1, 
                                  expect_channels = 0, 
                                  expect_clients = 2)
        irc_session.verify_motd(client1, "user1")           
        
    def test_connect_lusers_motd_unknown3(self, irc_session):
        """
        Test correct values in LUSERS with five clients connected,
        four of which are "unknown" (haven't completed its registration)
        """        
        unknown1 = irc_session.get_client()
        unknown2 = irc_session.get_client()
        unknown3 = irc_session.get_client()
        unknown4 = irc_session.get_client()
        
        time.sleep(0.05)

        client1 = irc_session.get_client()
        client1.send_cmd("NICK user1")
        client1.send_cmd("USER user1 * * :User One")

        irc_session.verify_welcome_messages(client1, "user1")
        irc_session.verify_lusers(client1, "user1", 
                                  expect_users = 1, 
                                  expect_ops = 0, 
                                  expect_unknown = 4, 
                                  expect_channels = 0, 
                                  expect_clients = 5)
        irc_session.verify_motd(client1, "user1")              



class TestLUSERS(object):
    
    @pytest.mark.category("LUSERS")
    def test_lusers1(self, irc_session):
        """
        Test calling LUSERS explicitly with one client.
        """   
        
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("LUSERS")     
        irc_session.verify_lusers(client1, "user1", 
                                  expect_users = 1, 
                                  expect_ops = 0, 
                                  expect_unknown = 0, 
                                  expect_channels = 0, 
                                  expect_clients = 1)           

    @pytest.mark.category("LUSERS")
    def test_lusers2(self, irc_session):
        """
        Test calling LUSERS explicitly with four clients.
        """   
        
        clients = irc_session.connect_clients(4)
        
        nick1, client1 = clients[0]
                        
        client1.send_cmd("LUSERS")     
        irc_session.verify_lusers(client1, nick1, 
                                  expect_users = 4, 
                                  expect_ops = 0, 
                                  expect_unknown = 0, 
                                  expect_channels = 0, 
                                  expect_clients = 4)           

    @pytest.mark.category("UPDATE_ASSIGNMENT2")
    def test_lusers_channels1(self, irc_session):
        """
        Test calling LUSERS with a server with nine users (user1-user9)
        where the users are in the following channels:
        
        #test1: user1, user2, user3
        #test2: user4, user5, user6
        #test3: user7, user8, user9                
        """   
        
        users = irc_session.connect_and_join_channels(channels1)
                
        users["user1"].send_cmd("LUSERS")
        irc_session.verify_lusers(users["user1"], "user1", 
                                  expect_users = 9, 
                                  expect_ops = 0, 
                                  expect_unknown = 0, 
                                  expect_channels = 3, 
                                  expect_clients = 9)           
        
    @pytest.mark.category("UPDATE_ASSIGNMENT2")
    def test_lusers_channels2(self, irc_session):
        """
        Test calling LUSERS with a server with eleven users (user1-user11)
        where the users are in the following channels:
        
        #test1: user1, user2, user3
        #test2: user4, user5, user6
        #test3: user7, user8, user9 
        
        Not in a channel: user10, user11               
        """    
        
        users = irc_session.connect_and_join_channels(channels2)
                
        users["user1"].send_cmd("LUSERS")
        irc_session.verify_lusers(users["user1"], "user1", 
                                  expect_users = 11, 
                                  expect_ops = 0, 
                                  expect_unknown = 0, 
                                  expect_channels = 3, 
                                  expect_clients = 11)    
        
    @pytest.mark.category("UPDATE_ASSIGNMENT2")
    def test_lusers_channels3(self, irc_session):
        """
        Test calling LUSERS with a server with eleven users (user1-user11)
        where the users are in the following channels:
        
        #test1: user1, user2, user3
        #test2: user2
        #test3: user3, user4, user5, user6
        #test4: user7, user8, user9, user1, user2
        #test5: user1, user5 
        
        Not in a channel: user10, user11               
        """   
        
        users = irc_session.connect_and_join_channels(channels3)
                
        users["user1"].send_cmd("LUSERS")
        irc_session.verify_lusers(users["user1"], "user1", 
                                  expect_users = 11, 
                                  expect_ops = 0, 
                                  expect_unknown = 0, 
                                  expect_channels = 5, 
                                  expect_clients = 11)    
        
    @pytest.mark.category("UPDATE_ASSIGNMENT2")
    def test_lusers_ircops1(self, irc_session):
        """
        Test calling LUSERS explicitly with four clients,
        one of which is a IRCop.
        """  
                       
        clients = irc_session.connect_clients(4)
        
        nick1, client1 = clients[0]
        nick2, client2 = clients[1]
            
        client1.send_cmd("OPER user1 %s" % irc_session.oper_password)
        irc_session.get_reply(client1, expect_code = replies.RPL_YOUREOPER)
                              
        client2.send_cmd("LUSERS")
        irc_session.verify_lusers(client2, nick2, 
                                  expect_users = 4, 
                                  expect_ops = 1, 
                                  expect_unknown = 0, 
                                  expect_channels = 0, 
                                  expect_clients = 4)       
        
    @pytest.mark.category("UPDATE_ASSIGNMENT2")
    def test_lusers_ircops2(self, irc_session):
        """
        Test calling LUSERS explicitly with four clients,
        two of which are IRCops. 
        """  
                       
        clients = irc_session.connect_clients(4)
        
        nick1, client1 = clients[0]
        nick2, client2 = clients[1]
        nick3, client3 = clients[2]
                        
        for nick, client in clients:
            client.send_cmd("LUSERS")
            irc_session.verify_lusers(client, nick, 
                                      expect_users = 4, 
                                      expect_ops = 0, 
                                      expect_unknown = 0, 
                                      expect_channels = 0, 
                                      expect_clients = 4)   

        client1.send_cmd("OPER user1 %s" % irc_session.oper_password)
        irc_session.get_reply(client1, expect_code = replies.RPL_YOUREOPER)                        
    
        for nick, client in clients:
            client.send_cmd("LUSERS")
            irc_session.verify_lusers(client, nick, 
                                      expect_users = 4, 
                                      expect_ops = 1, 
                                      expect_unknown = 0, 
                                      expect_channels = 0, 
                                      expect_clients = 4)           

        client2.send_cmd("OPER user2 %s" % irc_session.oper_password)
        irc_session.get_reply(client2, expect_code = replies.RPL_YOUREOPER)    
        
        for nick, client in clients:
            client.send_cmd("LUSERS")
            irc_session.verify_lusers(client, nick, 
                                      expect_users = 4, 
                                      expect_ops = 2, 
                                      expect_unknown = 0, 
                                      expect_channels = 0, 
                                      expect_clients = 4)               
        
    @pytest.mark.category("UPDATE_ASSIGNMENT2")
    def test_lusers_channels_and_ircops(self, irc_session):
        """
        Test calling LUSERS with a server with eleven users (user1-user11)
        where the users are in the following channels:
        
        #test1: user1, user2, user3
        #test2: user2
        #test3: user3, user4, user5, user6
        #test4: user7, user8, user9, user1, user2
        #test5: user1, user5 
        
        Not in a channel: user10, user11      
        
        Additionally, user2 and user5 are IRCops.         
        """   
        
        users = irc_session.connect_and_join_channels(channels3, ircops = ["user2", "user5"])
                
        users["user1"].send_cmd("LUSERS")
        irc_session.verify_lusers(users["user1"], "user1", 
                                  expect_users = 11, 
                                  expect_ops = 2, 
                                  expect_unknown = 0, 
                                  expect_channels = 5, 
                                  expect_clients = 11)           
        

@pytest.mark.category("MOTD")
class TestMOTD(object):
    
    def test_motd1(self, irc_session):
        """
        Test calling MOTD where the MOTD file contains the following
        (newlines are shown as "\n" and the end of the file as <EOF>):
        
        AAA\n
        BBB\n
        CCC\n
        DDD<EOF>
        
        """        
        
        client1 = irc_session.connect_user("user1", "User One")
        
        motd = """AAA
BBB
CCC
DDD"""

        motdf = open(irc_session.tmpdir + "/motd.txt", "w")
        motdf.write(motd)
        motdf.close()

        client1.send_cmd("MOTD")     
        irc_session.verify_motd(client1, "user1", expect_motd = motd)
        
    def test_motd2(self, irc_session):
        """
        Test calling MOTD where the MOTD file contains the following
        (newlines are shown as "\n" and the end of the file as <EOF>):
        
        AAA\n
        BBB\n
        CCC\n
        DDD\n
        <EOF>
        
        """   
                
        client1 = irc_session.connect_user("user1", "User One")
        
        motd = """AAA
BBB
CCC
DDD
"""

        motdf = open(irc_session.tmpdir + "/motd.txt", "w")
        motdf.write(motd)
        motdf.close()

        client1.send_cmd("MOTD")     
        irc_session.verify_motd(client1, "user1", expect_motd = motd)
        

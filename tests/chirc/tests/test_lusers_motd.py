import time
import pytest

@pytest.mark.category("LUSERS")
class TestConnectionWithLUSERSMOTD(object):

    def test_connect_lusers_motd1(self, irc_session):
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


@pytest.mark.category("LUSERS")
class TestLUSERS(object):
    
    def test_lusers(self, irc_session):
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("LUSERS")     
        irc_session.verify_lusers(client1, "user1", 
                                  expect_users = 1, 
                                  expect_ops = 0, 
                                  expect_unknown = 0, 
                                  expect_channels = 0, 
                                  expect_clients = 1)           

@pytest.mark.category("MOTD")
class TestMOTD(object):
    
    def test_motd1(self, irc_session):
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
        

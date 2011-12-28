import tests.replies as replies
import time
from tests.common import ChircTestCase, ChircClient
from tests.scores import score

class ConnectionWithLUSERSMOTD(ChircTestCase):

    @score(category="LUSERS")
    def test_connect_lusers_motd1(self):
        client = self.get_client()
        
        client.send_cmd("NICK user1")
        client.send_cmd("USER user1 * * :User One")
        
        self._test_welcome_messages(client, "user1")
        self._test_lusers(client, "user1", 
                          expect_users = 1, 
                          expect_ops = 0, 
                          expect_unknown = 0, 
                          expect_channels = 0, 
                          expect_clients = 1)

        self._test_motd(client, "user1")         
        
    @score(category="LUSERS")
    def test_connect_lusers_motd2(self):
        client = self.get_client()
        
        client.send_cmd("USER user1 * * :User One")
        client.send_cmd("NICK user1")
        
        self._test_welcome_messages(client, "user1")
        self._test_lusers(client, "user1", 
                          expect_users = 1, 
                          expect_ops = 0, 
                          expect_unknown = 0, 
                          expect_channels = 0, 
                          expect_clients = 1)

        self._test_motd(client, "user1")         
        

    @score(category="LUSERS")
    def test_connect_lusers_motd_2users(self):
        client1 = self.get_client()
        
        client1.send_cmd("NICK user1")
        client1.send_cmd("USER user1 * * :User One")

        self._test_welcome_messages(client1, "user1")
        self._test_lusers(client1, "user1", 
                          expect_users = 1, 
                          expect_ops = 0, 
                          expect_unknown = 0, 
                          expect_channels = 0, 
                          expect_clients = 1)
        self._test_motd(client1, "user1")         


        client2 = self.get_client()
        client2.send_cmd("NICK user2")
        client2.send_cmd("USER user2 * * :User Two")
        
        self._test_welcome_messages(client2, "user2")
        self._test_lusers(client2, "user2", 
                          expect_users = 2, 
                          expect_ops = 0, 
                          expect_unknown = 0, 
                          expect_channels = 0, 
                          expect_clients = 2)
        self._test_motd(client2, "user2")         

    @score(category="LUSERS")
    def test_connect_lusers_motd_unknown(self):
        unknown1 = self.get_client()
        time.sleep(0.05)
        
        client1 = self.get_client()
        client1.send_cmd("NICK user1")
        client1.send_cmd("USER user1 * * :User One")

        time.sleep(0.05)

        self._test_welcome_messages(client1, "user1")
        self._test_lusers(client1, "user1", 
                          expect_users = 1, 
                          expect_ops = 0, 
                          expect_unknown = 1, 
                          expect_channels = 0, 
                          expect_clients = 2)
        self._test_motd(client1, "user1")       
        
    @score(category="LUSERS")
    def test_connect_lusers_motd_unknown2(self):
        unknown1 = self.get_client()
        unknown1.send_cmd("NICK unknown1")
        time.sleep(0.05)
        
        client1 = self.get_client()
        client1.send_cmd("NICK user1")
        client1.send_cmd("USER user1 * * :User One")

        self._test_welcome_messages(client1, "user1")
        self._test_lusers(client1, "user1", 
                          expect_users = 1, 
                          expect_ops = 0, 
                          expect_unknown = 1, 
                          expect_channels = 0, 
                          expect_clients = 2)
        self._test_motd(client1, "user1")           
        
    @score(category="LUSERS")
    def test_connect_lusers_motd_unknown3(self):
        unknown1 = self.get_client()
        unknown2 = self.get_client()
        unknown3 = self.get_client()
        unknown4 = self.get_client()
        
        time.sleep(0.05)

        client1 = self.get_client()
        client1.send_cmd("NICK user1")
        client1.send_cmd("USER user1 * * :User One")

        self._test_welcome_messages(client1, "user1")
        self._test_lusers(client1, "user1", 
                          expect_users = 1, 
                          expect_ops = 0, 
                          expect_unknown = 4, 
                          expect_channels = 0, 
                          expect_clients = 5)
        self._test_motd(client1, "user1")              


class LUSERS(ChircTestCase):
    
    @score(category="LUSERS")
    def test_lusers(self):
        client1 = self._connect_user("user1", "User One")
        
        client1.send_cmd("LUSERS")     
        self._test_lusers(client1, "user1", 
                          expect_users = 1, 
                          expect_ops = 0, 
                          expect_unknown = 0, 
                          expect_channels = 0, 
                          expect_clients = 1)           


class MOTD(ChircTestCase):
    
    @score(category="MOTD")
    def test_motd1(self):
        client1 = self._connect_user("user1", "User One")
        
        motd = """AAA
BBB
CCC
DDD"""

        motdf = open(self.tmpdir + "/motd.txt", "w")
        motdf.write(motd)
        motdf.close()

        client1.send_cmd("MOTD")     
        self._test_motd(client1, "user1", expect_motd = motd)
        
    @score(category="MOTD")
    def test_motd2(self):
        client1 = self._connect_user("user1", "User One")
        
        motd = """AAA
BBB
CCC
DDD
"""

        motdf = open(self.tmpdir + "/motd.txt", "w")
        motdf.write(motd)
        motdf.close()

        client1.send_cmd("MOTD")     
        self._test_motd(client1, "user1", expect_motd = motd)
        

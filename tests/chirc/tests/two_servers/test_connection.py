import chirc.replies as replies
import pytest

from chirc.tests.common.fixtures import create_dummy_two_server_network, create_two_server_network
from chirc.types import ReplyTimeoutException


@pytest.mark.category("SERVER_REGISTRATION")
class TestServerRegistration(object):
    """
    These tests check the server registration commands (PASS and SERVER)
    by launching a single chirc server, and then using a client that
    acts as another server (to verify that the correct replies are sent
    in response to the server registration commands).

    We refer to the server that initiates the connection (i.e., the one
    sending the PASS and SERVER command) as the "active server" (although
    this one is emulated via a client) and the one receiving the PASS and
    SERVER commands as the "passive server"
    """

    def test_server_registration_simple1(self, irc_network_session):
        """
        Checks that PASS and SERVER commands are accepted
        """

        irc_network_session.set_servers(2)
        irc_network_session.start_session(0)
        passive_server = irc_network_session.servers[0]
        active_server = irc_network_session.servers[1]

        irc_session = passive_server.irc_session
        client = irc_session.get_client()

        client.send_cmd("PASS {} 0210 chirc|test".format(passive_server.passwd))
        irc_session.get_reply(client, expect_timeout=True)

        client.send_cmd("SERVER {} 1 1 :Test".format(active_server.servername))

        irc_session.verify_server_registration(client, passive_server, active_server)

    def test_server_registration_simple2(self, irc_network_session):
        """
        Checks that PASS and SERVER commands are accepted (sending SERVER first)
        """

        irc_network_session.set_servers(2)
        irc_network_session.start_session(0)
        passive_server = irc_network_session.servers[0]
        active_server = irc_network_session.servers[1]

        irc_session = passive_server.irc_session
        client = irc_session.get_client()

        client.send_cmd("SERVER {} 1 1 :Test".format(active_server.servername))
        irc_session.get_reply(client, expect_timeout=True)

        client.send_cmd("PASS {} 0210 chirc|test".format(passive_server.passwd))

        irc_session.verify_server_registration(client, passive_server, active_server)


    def test_server_registration_wrong_password(self, irc_network_session):
        """
        Checks that an incorrect password is rejected
        """

        irc_network_session.set_servers(2)
        irc_network_session.start_session(0)
        passive_server = irc_network_session.servers[0]
        active_server = irc_network_session.servers[1]

        irc_session = passive_server.irc_session
        client = irc_session.get_client()

        client.send_cmd("PASS wrongpassword 0210 chirc|test")
        irc_session.get_reply(client, expect_timeout=True)

        client.send_cmd("SERVER {} 1 1 :Test".format(active_server.servername))

        reply = irc_session.get_message(client, expect_prefix = False, expect_cmd = "ERROR",
                                        expect_nparams = 1,
                                        long_param_re = "Bad password")

    def test_server_registration_wrong_servername(self, irc_network_session):
        """
        Checks that an incorrect servername is rejected
        """

        irc_network_session.set_servers(2)
        irc_network_session.start_session(0)
        passive_server = irc_network_session.servers[0]
        active_server = irc_network_session.servers[1]

        irc_session = passive_server.irc_session
        client = irc_session.get_client()

        # We also send a bad password to make sure we don't get a bad password reply
        client.send_cmd("PASS wrongpassword 0210 chirc|test")
        irc_session.get_reply(client, expect_timeout=True)

        client.send_cmd("SERVER wrongserver 1 1 :Test")

        reply = irc_session.get_message(client, expect_prefix = False, expect_cmd = "ERROR",
                                        expect_nparams = 1,
                                        long_param_re = "Server not configured here")

    def test_server_registration_server_already_registered(self, irc_network_session):
        """
        Checks that we can't register a server twice (from a separate connection)
        """

        irc_network_session.set_servers(2)
        irc_network_session.start_session(0)
        passive_server = irc_network_session.servers[0]
        active_server = irc_network_session.servers[1]

        irc_session = passive_server.irc_session
        client1 = irc_session.get_client()
        client2 = irc_session.get_client()

        client1.send_cmd("PASS {} 0210 chirc|test".format(passive_server.passwd))
        irc_session.get_reply(client1, expect_timeout=True)

        client1.send_cmd("SERVER {} 1 1 :Test".format(active_server.servername))

        irc_session.verify_server_registration(client1, passive_server, active_server)

        client2.send_cmd("PASS {} 0210 chirc|test".format(passive_server.passwd))
        irc_session.get_reply(client2, expect_timeout=True)

        client2.send_cmd("SERVER {} 1 1 :Test".format(active_server.servername))

        reply = irc_session.get_message(client2, expect_prefix = False, expect_cmd = "ERROR",
                                        expect_nparams = 1,
                                        long_param_re = 'ID "{}" already registered'.format(active_server.servername))

    def test_server_registration_connection_already_registered1(self, irc_network_session):
        """
        Checks that, after sending PASS and SERVER, we can't send those commands again from
        the same connection.
        """

        rv = create_dummy_two_server_network(irc_network_session)

        passive_server, active_server, active_client, _, _ = rv
        irc_session = passive_server.irc_session

        active_client.send_cmd("PASS {} 0210 chirc|test".format(passive_server.passwd))

        reply = irc_session.get_reply(active_client, expect_code = replies.ERR_ALREADYREGISTRED, expect_nick = active_server.servername,
                                      expect_nparams = 1, long_param_re = r"Unauthorized command \(already registered\)")

    def test_server_registration_connection_already_registered2(self, irc_network_session):
        """
        Checks that, after sending PASS and SERVER, we can't send those commands again from
        the same connection.
        """

        rv = create_dummy_two_server_network(irc_network_session)

        passive_server, active_server, active_client, _, _ = rv
        irc_session = passive_server.irc_session

        active_client.send_cmd("SERVER {} 1 1 :Test".format(active_server.servername))

        reply = irc_session.get_reply(active_client, expect_code = replies.ERR_ALREADYREGISTRED, expect_nick = active_server.servername,
                                      expect_nparams = 1, long_param_re = r"Unauthorized command \(already registered\)")


@pytest.mark.category("CONNECT")
class TestServerConnect(object):
    """
    This test check that the CONNECT command correctly connects two servers.

    There are additional tests in other files that perform additional actions
    after the CONNECT message to verify that the connection is working as expected,
    so this test will still pass even if CONNECT doesn't result in a connection
    actually being established between the servers.
    """

    def test_server_connect(self, irc_network_session):
        """
        Check that the CONNECT command works correctly
        """

        # Everything happens inside this function.
        create_two_server_network(irc_network_session)

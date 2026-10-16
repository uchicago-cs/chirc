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
        Checks that a SERVER command sent before PASS is rejected
        (the PASS command must be sent first, so no password was given)
        """

        irc_network_session.set_servers(2)
        irc_network_session.start_session(0)
        passive_server = irc_network_session.servers[0]
        active_server = irc_network_session.servers[1]

        irc_session = passive_server.irc_session
        client = irc_session.get_client()

        client.send_cmd("SERVER {} 1 1 :Test".format(active_server.servername))

        irc_session.get_message(client, expect_prefix = False, expect_cmd = "ERROR",
                                expect_nparams = 1,
                                long_param_re = "Bad password")

        # The passive server must close the connection after sending the ERROR
        irc_session.verify_disconnected(client)


    def test_server_registration_multiple_pass1(self, irc_network_session):
        """
        Checks that, if multiple PASS commands are sent, only the last one counts
        (an incorrect password followed by the correct one is accepted)
        """

        irc_network_session.set_servers(2)
        irc_network_session.start_session(0)
        passive_server = irc_network_session.servers[0]
        active_server = irc_network_session.servers[1]

        irc_session = passive_server.irc_session
        client = irc_session.get_client()

        client.send_cmd("PASS wrongpassword 0210 chirc|test")
        irc_session.get_reply(client, expect_timeout=True)

        client.send_cmd("PASS {} 0210 chirc|test".format(passive_server.passwd))
        irc_session.get_reply(client, expect_timeout=True)

        client.send_cmd("SERVER {} 1 1 :Test".format(active_server.servername))

        irc_session.verify_server_registration(client, passive_server, active_server)


    def test_server_registration_multiple_pass2(self, irc_network_session):
        """
        Checks that, if multiple PASS commands are sent, only the last one counts
        (the correct password followed by an incorrect one is rejected)
        """

        irc_network_session.set_servers(2)
        irc_network_session.start_session(0)
        passive_server = irc_network_session.servers[0]
        active_server = irc_network_session.servers[1]

        irc_session = passive_server.irc_session
        client = irc_session.get_client()

        client.send_cmd("PASS {} 0210 chirc|test".format(passive_server.passwd))
        irc_session.get_reply(client, expect_timeout=True)

        client.send_cmd("PASS wrongpassword 0210 chirc|test")
        irc_session.get_reply(client, expect_timeout=True)

        client.send_cmd("SERVER {} 1 1 :Test".format(active_server.servername))

        irc_session.get_message(client, expect_prefix = False, expect_cmd = "ERROR",
                                expect_nparams = 1,
                                long_param_re = "Bad password")

        # The passive server must close the connection after sending the ERROR
        irc_session.verify_disconnected(client)


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

        # The passive server must close the connection after sending the ERROR
        irc_session.verify_disconnected(client)

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

        # We send the correct password, so the server name is the only error
        # (the specification doesn't say in what order the checks are done)
        client.send_cmd("PASS {} 0210 chirc|test".format(passive_server.passwd))
        irc_session.get_reply(client, expect_timeout=True)

        client.send_cmd("SERVER wrongserver 1 1 :Test")

        reply = irc_session.get_message(client, expect_prefix = False, expect_cmd = "ERROR",
                                        expect_nparams = 1,
                                        long_param_re = "Server not configured here")

        # The passive server must close the connection after sending the ERROR
        irc_session.verify_disconnected(client)

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

        # The passive server must close the connection after sending the ERROR
        irc_session.verify_disconnected(client2)

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


    def _connect_user_to_passive(self, irc_network_session, oper=False):
        irc_network_session.set_servers(2)
        irc_network_session.start_session(0)
        passive_server = irc_network_session.servers[0]
        active_server = irc_network_session.servers[1]

        irc_session = passive_server.irc_session
        client = irc_session.connect_user("user1", "User One")

        if oper:
            client.send_cmd("OPER user1 {}".format(irc_session.oper_password))
            irc_session.get_reply(client, expect_code = replies.RPL_YOUREOPER, expect_nick = "user1",
                                  expect_nparams = 1, long_param_re = "You are now an IRC operator")

        return irc_session, active_server, client

    def test_server_connect_not_oper(self, irc_network_session):
        """
        Check that only IRC operators can send a CONNECT command
        """

        irc_session, active_server, client = self._connect_user_to_passive(irc_network_session)

        client.send_cmd("CONNECT {} 0".format(active_server.servername))

        irc_session.get_reply(client, expect_code = replies.ERR_NOPRIVILEGES, expect_nick = "user1",
                              expect_nparams = 1,
                              long_param_re = "Permission Denied- You're not an IRC operator")

    def test_server_connect_no_such_server(self, irc_network_session):
        """
        Check that a CONNECT to a server that is not in the network
        specification file results in an ERR_NOSUCHSERVER reply
        """

        irc_session, active_server, client = self._connect_user_to_passive(irc_network_session, oper=True)

        client.send_cmd("CONNECT nosuchserver.example.net 0")

        irc_session.get_reply(client, expect_code = replies.ERR_NOSUCHSERVER, expect_nick = "user1",
                              expect_nparams = 2, expect_short_params = ["nosuchserver.example.net"],
                              long_param_re = "No such server")

    def test_server_connect_need_more_params(self, irc_network_session):
        """
        Check that a CONNECT with too few parameters results in an
        ERR_NEEDMOREPARAMS reply
        """

        irc_session, active_server, client = self._connect_user_to_passive(irc_network_session, oper=True)

        client.send_cmd("CONNECT {}".format(active_server.servername))

        irc_session.get_ERR_NEEDMOREPARAMS_reply(client, expect_nick = "user1", expect_cmd = "CONNECT")

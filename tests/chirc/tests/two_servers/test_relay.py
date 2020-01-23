import chirc.replies as replies
import pytest

from chirc.tests.common.fixtures import create_dummy_two_server_network, create_two_server_network
from chirc.types import ReplyTimeoutException


@pytest.mark.category("NETWORK_RELAY_NO_CONNECT")
class TestNetworkRelayNoConnect(object):
    """
    These tests check that certain relays work correctly between two servers,
    but does so by launching a single chirc server, and then using a client that
    acts as another server (to verify that the correct replies are sent
    in response to the server registration commands).

    We refer to the server that initiates the connection (i.e., the one
    sending the PASS and SERVER command) as the "active server" (although
    this one is emulated via a client) and the one receiving the PASS and
    SERVER commands as the "passive server"
    """

    def test_network_relay_new_user1(self, irc_network_session):
        """
        Checks that a NICK message is relayed to the active server
        when a user connects to the passive server.
        """

        # The verification of the relayed NICK is done inside this function
        _ = create_dummy_two_server_network(irc_network_session,
                                             num_clients_to_passive=1)


    def test_network_relay_new_user2(self, irc_network_session):
        """
        Checks that NICK messages are relayed to the active server
        when multiple users connect to the passive server.
        """

        # The verification of the relayed NICKs is done inside this function
        _ = create_dummy_two_server_network(irc_network_session,
                                            num_clients_to_passive=5)

    def test_network_relay_new_user3(self, irc_network_session):
        """
        Simulate a user connecting to the active server by sending a NICK
        message to the passive server.
        """

        # The NICK message is sent inside this function
        _ = create_dummy_two_server_network(irc_network_session,
                                            num_dummy_users_in_active=1)


    def test_network_relay_new_user4(self, irc_network_session):
        """
        Simulate a user connecting to the active server by sending multiple NICK
        messages to the passive server.
        """

        # The NICK messages are sent inside this function
        _ = create_dummy_two_server_network(irc_network_session,
                                            num_dummy_users_in_active=5)


    def test_network_relay_privmsg1(self, irc_network_session):
        """
        Check that a PRIVMSG sent from a user in the passive server
        to a user in the active server is relayed correctly
        """

        rv = create_dummy_two_server_network(irc_network_session,
                                             num_clients_to_passive=1,
                                             num_dummy_users_in_active=1)

        passive_server, active_server, active_client, clients_to_passive, dummy_active_nicks = rv
        irc_session = passive_server.irc_session

        from_nick, from_client = clients_to_passive[0]
        to_nick = dummy_active_nicks[0]

        from_client.send_cmd("PRIVMSG {} :Hello".format(to_nick))

        irc_session.verify_relayed_privmsg(active_client, from_nick=from_nick, recip=to_nick, msg="Hello")

    def test_network_relay_privmsg2(self, irc_network_session):
        """
        Check that a PRIVMSG sent to a user in the same server is not
        relayed to the other server
        """

        rv = create_dummy_two_server_network(irc_network_session,
                                             num_clients_to_passive=2,
                                             num_dummy_users_in_active=1)

        passive_server, active_server, active_client, clients_to_passive, dummy_active_nicks = rv
        irc_session = passive_server.irc_session

        nick1, client1 = clients_to_passive[0]
        nick2, client2 = clients_to_passive[1]

        client1.send_cmd("PRIVMSG {} :Hello".format(nick2))

        irc_session.verify_relayed_privmsg(client2, from_nick=nick1, recip=nick2, msg="Hello")

        irc_session.get_reply(active_client, expect_timeout=True)


    def test_network_relay_privmsg3(self, irc_network_session):
        """
        Check that a PRIVMSG sent from a user in the active server
        to a user in the passive server is relayed correctly
        """

        rv = create_dummy_two_server_network(irc_network_session,
                                             num_clients_to_passive=1,
                                             num_dummy_users_in_active=1)

        passive_server, active_server, active_client, clients_to_passive, dummy_active_nicks = rv
        irc_session = passive_server.irc_session

        to_nick, to_client = clients_to_passive[0]
        from_nick = dummy_active_nicks[0]

        active_client.send_cmd(":{} PRIVMSG {} :Hello".format(from_nick, to_nick))
        irc_session.verify_relayed_privmsg(to_client, from_nick=from_nick, recip=to_nick, msg="Hello")

        irc_session.get_reply(active_client, expect_timeout=True)


    def test_network_relay_join1(self, irc_network_session):
        """
        Check that a JOIN in the passive server is relayed to the active server
        """

        rv = create_dummy_two_server_network(irc_network_session,
                                             num_clients_to_passive=1,
                                             num_dummy_users_in_active=1)

        passive_server, active_server, active_client, clients_to_passive, dummy_active_nicks = rv
        irc_session = passive_server.irc_session

        nick1, client1 = clients_to_passive[0]
        nick101 = dummy_active_nicks[0]

        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, nick1, "#test")

        irc_session.verify_relayed_join(active_client, from_nick="user1", channel="#test")


    def test_network_relay_join2(self, irc_network_session):
        """
        Check that two JOINs in the passive server are relayed to the active server
        """

        rv = create_dummy_two_server_network(irc_network_session,
                                             num_clients_to_passive=2,
                                             num_dummy_users_in_active=1)

        passive_server, active_server, active_client, clients_to_passive, dummy_active_nicks = rv
        irc_session = passive_server.irc_session

        nick1, client1 = clients_to_passive[0]
        nick2, client2 = clients_to_passive[1]
        nick101 = dummy_active_nicks[0]

        irc_session.join_channel(clients_to_passive, "#test")

        irc_session.verify_relayed_join(active_client, from_nick="user1", channel="#test")
        irc_session.verify_relayed_join(active_client, from_nick="user2", channel="#test")

        active_client.send_cmd(":{} JOIN #test".format(nick101))
        irc_session.verify_relayed_join(client1, from_nick=nick101, channel="#test")
        irc_session.verify_relayed_join(client2, from_nick=nick101, channel="#test")

        irc_session.get_reply(active_client, expect_timeout=True)

    def test_network_relay_privmsg_channel1(self, irc_network_session):
        """
        Check that a PRIVMSG to a channel (sent from a user connected
        to the passive server) is relayed to the active server
        """

        rv = create_dummy_two_server_network(irc_network_session,
                                             num_clients_to_passive=1,
                                             num_dummy_users_in_active=1)

        passive_server, active_server, active_client, clients_to_passive, dummy_active_nicks = rv
        irc_session = passive_server.irc_session

        nick1, client1 = clients_to_passive[0]
        nick101 = dummy_active_nicks[0]

        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, nick1, "#test")

        irc_session.verify_relayed_join(active_client, from_nick="user1", channel="#test")

        client1.send_cmd("PRIVMSG #test :Hello channel")

        irc_session.verify_relayed_privmsg(active_client, from_nick=nick1, recip="#test", msg="Hello channel")


    def test_network_relay_privmsg_channel2(self, irc_network_session):
        """
        In this test, a user on the passive server creates a channel.
        We then simulate a user in the active server joining that channel
        and sending a message to that channel. We verify that the user
        on the passive server receives that message.
        """

        rv = create_dummy_two_server_network(irc_network_session,
                                             num_clients_to_passive=1,
                                             num_dummy_users_in_active=1)

        passive_server, active_server, active_client, clients_to_passive, dummy_active_nicks = rv
        irc_session = passive_server.irc_session

        nick1, client1 = clients_to_passive[0]
        nick101 = dummy_active_nicks[0]

        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, nick1, "#test")
        irc_session.verify_relayed_join(active_client, from_nick=nick1, channel="#test")

        active_client.send_cmd(":{} JOIN #test".format(nick101))
        irc_session.verify_relayed_join(client1, from_nick=nick101, channel="#test")

        active_client.send_cmd(":{} PRIVMSG #test :Hello channel".format(nick101))
        irc_session.verify_relayed_privmsg(client1, from_nick=nick101, recip="#test", msg="Hello channel")

        irc_session.get_reply(active_client, expect_timeout=True)


@pytest.mark.category("NETWORK_RELAY_CONNECT")
class TestNetworkRelayConnect(object):
    """
    These tests check that certain relays work correctly between two servers.
    We launch two servers, and have one connect to the other (by sending a
    CONNECT command)

    We refer to the server that initiates the connection (i.e., the one
    receiving the CONNECT command) as the "active server" and the
    other one as the "passive server"
    """

    def test_network_relay_connect_privmsg1(self, irc_network_session):
        """
        Check that a PRIVMSG sent to a user in a different server is relayed correctly.
        More specifically, a user in the passive server wants to send a message
        to a user that is connected to the active server.
        """

        rv = create_two_server_network(irc_network_session,
                                       num_clients_to_passive=1,
                                       num_clients_to_active=1)

        passive_server, active_server, clients_to_passive, clients_to_active = rv

        from_nick, from_client = clients_to_passive[0]
        to_nick, to_client = clients_to_active[0]

        from_client.send_cmd("PRIVMSG {} :Hello".format(to_nick))

        active_server.irc_session.verify_relayed_privmsg(to_client, from_nick=from_nick, recip=to_nick, msg="Hello")

    def test_network_relay_connect_privmsg_channel1(self, irc_network_session):
        """
        Check that a PRIVMSG to a channel is relayed correctly.
        More specifically, a client on the passive server joins a channel,
        a client on the active server joins that same channel, and then
        the client on the passive server sends a message to the channel.
        That message should then be relayed to the user on the active server.
        """

        rv = create_two_server_network(irc_network_session,
                                       num_clients_to_passive=1,
                                       num_clients_to_active=1)

        passive_server, active_server, clients_to_passive, clients_to_active = rv

        from_nick, from_client = clients_to_passive[0]
        to_nick, to_client = clients_to_active[0]

        from_client.send_cmd("JOIN #test")
        passive_server.irc_session.verify_join(from_client, from_nick, "#test")

        to_client.send_cmd("JOIN #test")
        active_server.irc_session.verify_join(to_client, to_nick, "#test")

        from_client.send_cmd("PRIVMSG #test :Hello channel")

        active_server.irc_session.verify_relayed_privmsg(to_client, from_nick=from_nick, recip="#test", msg="Hello channel")
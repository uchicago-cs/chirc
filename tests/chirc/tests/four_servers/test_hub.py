import pytest

from chirc.tests.common.fixtures import create_dummy_hub_network, create_hub_network, \
    settle, nick_known, channel_known


@pytest.mark.category("NETWORK_HUB_SPOKE")
class TestNetworkHubSpoke(object):
    """
    These tests check a four-server network with a hub-and-spoke topology,
    where server A (irc-1.example.net) is the hub, and servers B, C, and D
    (irc-2, irc-3, and irc-4) each connect to A:

                B
                |
            C - A - D
    """

    def test_hub_registration(self, irc_network_session):
        """
        Only the hub (A) is running, and three clients act as the spoke
        servers (B, C, D). Checks that the hub accepts the PASS and SERVER
        commands from all three of them.
        """

        # The verification of the server registrations is done inside this function
        _ = create_dummy_hub_network(irc_network_session)


    def test_hub_relay_new_user(self, irc_network_session):
        """
        Only the hub (A) is running, and three clients act as the spoke
        servers (B, C, D). Checks that, when a user connects to the hub,
        the NICK message is relayed to all three spoke servers.
        """

        # The verification of the relayed NICKs is done inside this function
        _ = create_dummy_hub_network(irc_network_session, num_clients_to_hub=1)


    def test_hub_connect(self, irc_network_session):
        """
        All four servers are running, and the spoke servers (B, C, D) each
        connect to the hub (A) using CONNECT. This only checks that the
        connections can be made without anything failing (CONNECT does not
        return anything on success).
        """

        # Everything happens inside this function.
        create_hub_network(irc_network_session)


    def test_hub_connect_privmsg(self, irc_network_session):
        """
        All four servers are running, and the spoke servers (B, C, D) each
        connect to the hub (A) using CONNECT. A user then connects to the hub,
        and one user connects to each spoke. Each spoke user sends a PRIVMSG
        to the hub user, which will only arrive if the spoke knows about the
        hub user (i.e., the hub relayed its NICK) and the link to the hub works.
        """

        rv = create_hub_network(irc_network_session, num_clients_to_hub=1)
        hub_server, spoke_servers, _, clients_to_hub = rv

        nick1, client1 = clients_to_hub[0]

        # These users connect after the servers are linked, so their
        # NICKs are relayed to the hub (which needs to know about them
        # to deliver their PRIVMSGs)
        spoke_users = []
        for i, spoke_server in enumerate(spoke_servers):
            nick = "user%i" % (i+2)
            client = spoke_server.irc_session.connect_user(nick, "User %s" % nick)
            spoke_users.append( (nick, client) )

        # Wait until the hub knows about the spoke users
        for nick, client in spoke_users:
            settle(hub_server.irc_session, client1,
                   lambda: nick_known(hub_server.irc_session, client1, nick))

        for nick, client in spoke_users:
            client.send_cmd("PRIVMSG {} :Hello from {}".format(nick1, nick))
            hub_server.irc_session.verify_relayed_privmsg(client1, from_nick=nick, recip=nick1,
                                                          msg="Hello from {}".format(nick))


    #
    # Relaying messages from one spoke to another (through the hub)
    #

    def _introduce_spoke_user(self, irc_session, spoke_servers, spoke_clients, idx, nick):
        """
        Has the pretend spoke server with index `idx` introduce a new user
        (with a server-to-server NICK). The hub must relay the NICK to the
        other spokes (increasing the hopcount and keeping the prefix), but
        not back to the spoke it came from.
        """
        spoke_server = spoke_servers[idx]
        username = "User %s" % nick

        cmd = ":{} NICK {} 1 {} 127.0.0.1 1 + :{}".format(spoke_server.servername, nick, nick, username)
        spoke_clients[idx].send_cmd(cmd)

        for i, spoke_client in enumerate(spoke_clients):
            if i == idx:
                continue
            irc_session.verify_relayed_network_nick(spoke_client,
                                                    from_server=spoke_server,
                                                    expect_nick=nick,
                                                    expect_hopcount="2",
                                                    expect_username=nick,
                                                    expect_servertoken=None,
                                                    expect_mode="+",
                                                    expect_fullname=username)

        # The NICK must not be relayed back to the spoke it came from
        irc_session.get_reply(spoke_clients[idx], expect_timeout=True)

    def test_hub_relay_spoke_user(self, irc_network_session):
        """
        Only the hub (A) is running, and three clients act as the spoke
        servers (B, C, D). Checks that, when spoke B introduces a new user,
        the hub relays the NICK to spokes C and D (with the hopcount increased
        by one), but not back to B.
        """

        hub_server, spoke_servers, spoke_clients, _ = create_dummy_hub_network(irc_network_session)

        # The verification of the relayed NICKs is done inside this function
        self._introduce_spoke_user(hub_server.irc_session, spoke_servers, spoke_clients, 0, "user201")

    def test_hub_relay_privmsg_spoke_to_spoke(self, irc_network_session):
        """
        Only the hub (A) is running, and three clients act as the spoke
        servers (B, C, D). A user on spoke B sends a PRIVMSG to a user on
        spoke C. Checks that the hub relays it to C (and not back to B).
        """

        hub_server, spoke_servers, spoke_clients, _ = create_dummy_hub_network(irc_network_session)
        irc_session = hub_server.irc_session

        self._introduce_spoke_user(irc_session, spoke_servers, spoke_clients, 0, "user201")
        self._introduce_spoke_user(irc_session, spoke_servers, spoke_clients, 1, "user301")

        spoke_clients[0].send_cmd(":user201 PRIVMSG user301 :Hello")

        irc_session.verify_relayed_privmsg(spoke_clients[1], from_nick="user201", recip="user301",
                                           msg="Hello", expect_nick_only_prefix=True)

        # The PRIVMSG must not be relayed back to the spoke it came from
        irc_session.get_reply(spoke_clients[0], expect_timeout=True)

    def test_hub_relay_privmsg_channel_spoke_to_spoke(self, irc_network_session):
        """
        Only the hub (A) is running, and three clients act as the spoke
        servers (B, C, D). A user on spoke B and a user on spoke C join
        the same channel, and the user on B sends a PRIVMSG to the channel.
        Checks that the JOINs and the PRIVMSG are relayed to C
        (and not back to B).
        """

        hub_server, spoke_servers, spoke_clients, _ = create_dummy_hub_network(irc_network_session)
        irc_session = hub_server.irc_session

        self._introduce_spoke_user(irc_session, spoke_servers, spoke_clients, 0, "user201")
        self._introduce_spoke_user(irc_session, spoke_servers, spoke_clients, 1, "user301")

        spoke_clients[0].send_cmd(":user201 JOIN #test")
        irc_session.verify_relayed_join(spoke_clients[1], from_nick="user201", channel="#test",
                                        expect_nick_only_prefix=True)
        irc_session.verify_relayed_join(spoke_clients[2], from_nick="user201", channel="#test",
                                        expect_nick_only_prefix=True)
        irc_session.get_reply(spoke_clients[0], expect_timeout=True)

        spoke_clients[1].send_cmd(":user301 JOIN #test")
        irc_session.verify_relayed_join(spoke_clients[0], from_nick="user301", channel="#test",
                                        expect_nick_only_prefix=True)
        irc_session.verify_relayed_join(spoke_clients[2], from_nick="user301", channel="#test",
                                        expect_nick_only_prefix=True)
        irc_session.get_reply(spoke_clients[1], expect_timeout=True)

        spoke_clients[0].send_cmd(":user201 PRIVMSG #test :Hello channel")
        irc_session.verify_relayed_privmsg(spoke_clients[1], from_nick="user201", recip="#test",
                                           msg="Hello channel", expect_nick_only_prefix=True)

        # The PRIVMSG must not be relayed back to the spoke it came from
        irc_session.get_reply(spoke_clients[0], expect_timeout=True)

    def _connect_spoke_users(self, spoke_servers):
        """
        Connects one user to each spoke (after the servers are linked,
        so their NICKs are relayed to the rest of the network)
        """
        spoke_users = []
        for i, spoke_server in enumerate(spoke_servers):
            nick = "user%i" % (i+2)
            client = spoke_server.irc_session.connect_user(nick, "User %s" % nick)
            spoke_users.append( (nick, client) )

        # Wait until every spoke knows about the users on the other spokes
        # (their NICKs are relayed through the hub)
        for i, (nick, _) in enumerate(spoke_users):
            for j, (_, client) in enumerate(spoke_users):
                if i != j:
                    session = spoke_servers[j].irc_session
                    settle(session, client, lambda: nick_known(session, client, nick))

        return spoke_users

    def test_hub_connect_privmsg_spoke_to_spoke(self, irc_network_session):
        """
        All four servers are running, and the spoke servers (B, C, D) each
        connect to the hub (A) using CONNECT. A user on spoke B sends a
        PRIVMSG to a user on spoke C, which must be relayed through the hub.
        """

        hub_server, spoke_servers, _, _ = create_hub_network(irc_network_session)
        spoke_users = self._connect_spoke_users(spoke_servers)

        nick_b, client_b = spoke_users[0]
        nick_c, client_c = spoke_users[1]

        client_b.send_cmd("PRIVMSG {} :Hello from B".format(nick_c))
        spoke_servers[1].irc_session.verify_relayed_privmsg(client_c, from_nick=nick_b, recip=nick_c,
                                                            msg="Hello from B")

    def test_hub_connect_privmsg_channel_spoke_to_spoke(self, irc_network_session):
        """
        All four servers are running, and the spoke servers (B, C, D) each
        connect to the hub (A) using CONNECT. A user on spoke B and a user on
        spoke C join the same channel, and the user on B sends a PRIVMSG to the
        channel, which must be relayed through the hub.
        """

        hub_server, spoke_servers, _, _ = create_hub_network(irc_network_session)
        spoke_users = self._connect_spoke_users(spoke_servers)

        nick_b, client_b = spoke_users[0]
        nick_c, client_c = spoke_users[1]
        session_b = spoke_servers[0].irc_session
        session_c = spoke_servers[1].irc_session

        client_b.send_cmd("JOIN #test")
        session_b.verify_join(client_b, nick_b, "#test")

        # Wait until the JOIN has been relayed to C (through the hub)
        settle(session_c, client_c, lambda: channel_known(session_c, client_c, "#test"))

        client_c.send_cmd("JOIN #test")
        session_c.verify_join(client_c, nick_c, "#test")
        session_b.verify_relayed_join(client_b, from_nick=nick_c, channel="#test")

        client_b.send_cmd("PRIVMSG #test :Hello from B")
        session_c.verify_relayed_privmsg(client_c, from_nick=nick_b, recip="#test", msg="Hello from B")

    def test_hub_connect_list(self, irc_network_session):
        """
        All four servers are running, and the spoke servers (B, C, D) each
        connect to the hub (A) using CONNECT. A user on spoke B joins a channel.
        Checks that a user on spoke D sees that channel in LIST (which requires
        the JOIN to be relayed through the hub).
        """

        hub_server, spoke_servers, _, _ = create_hub_network(irc_network_session)
        spoke_users = self._connect_spoke_users(spoke_servers)

        nick_b, client_b = spoke_users[0]
        nick_d, client_d = spoke_users[2]

        client_b.send_cmd("JOIN #test")
        spoke_servers[0].irc_session.verify_join(client_b, nick_b, "#test")

        # The JOIN has to be relayed through the hub, so we may have to retry
        spoke_servers[2].irc_session.verify_list_eventually({"#test": (nick_b,)}, client_d, nick_d)

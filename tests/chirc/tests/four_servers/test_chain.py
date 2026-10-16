import chirc.replies as replies
import pytest

from chirc.tests.common.fixtures import create_chain_network, \
    settle, nick_known, channel_known, server_link_count


@pytest.mark.category("NETWORK_CHAIN")
class TestNetworkChain(object):
    """
    These tests check a four-server network where the servers are connected
    in sequence:

        A - B - C - D

    (B connects to A, C connects to B, and D connects to C)
    """

    def test_chain_privmsg(self, irc_network_session):
        """
        A user connects to A, and another user connects to D. Checks that
        a PRIVMSG from the user in A reaches the user in D (which requires
        relaying the users' NICKs, and the PRIVMSG, across the whole chain).
        """

        servers = create_chain_network(irc_network_session)
        server_a = servers[0]
        server_d = servers[3]

        nick_a = "user1"
        client_a = server_a.irc_session.connect_user(nick_a, "User One")

        nick_d = "user4"
        client_d = server_d.irc_session.connect_user(nick_d, "User Four")

        # Wait until A knows about the user on D, and D knows about the user
        # on A (their NICKs are relayed across the whole chain)
        settle(server_a.irc_session, client_a, lambda: nick_known(server_a.irc_session, client_a, nick_d))
        settle(server_d.irc_session, client_d, lambda: nick_known(server_d.irc_session, client_d, nick_a))

        client_a.send_cmd("PRIVMSG {} :Hello from A".format(nick_d))

        server_d.irc_session.verify_relayed_privmsg(client_d, from_nick=nick_a, recip=nick_d,
                                                    msg="Hello from A")

    def _connect_end_users(self, servers):
        """
        Connects a user to A and a user to D (after the servers are linked)
        """
        server_a, server_d = servers[0], servers[3]
        nick_a, nick_d = "user1", "user4"
        client_a = server_a.irc_session.connect_user(nick_a, "User One")
        client_d = server_d.irc_session.connect_user(nick_d, "User Four")

        # Wait until A knows about the user on D, and D knows about the user
        # on A (their NICKs are relayed across the whole chain)
        settle(server_a.irc_session, client_a, lambda: nick_known(server_a.irc_session, client_a, nick_d))
        settle(server_d.irc_session, client_d, lambda: nick_known(server_d.irc_session, client_d, nick_a))

        return ("user1", client_a), ("user4", client_d)

    def test_chain_hopcount(self, irc_network_session):
        """
        Servers A, B, and C are running, and connected in sequence (B connects
        to A, C connects to B). A client acts as server D, and connects to C.
        Checks that, when a user connects to A, the NICK that reaches D has
        a hopcount of 3 (and still has A's server name as its prefix).
        """

        irc_network_session.set_servers(4)
        servers = irc_network_session.servers
        for i in range(3):
            irc_network_session.start_session(i)

        for i in range(1, 3):
            server = servers[i]
            nick = "ircop%i" % (i+1)
            ircop_client = server.irc_session.connect_user(nick, "IRC Operator")
            ircop_client.send_cmd("OPER {} {}".format(nick, server.irc_session.oper_password))
            server.irc_session.get_reply(ircop_client, expect_code = replies.RPL_YOUREOPER,
                                         expect_nick = nick, expect_nparams = 1,
                                         long_param_re = "You are now an IRC operator")
            ircop_client.send_cmd("CONNECT {} 0".format(servers[i-1].servername))
            # CONNECT doesn't return anything on success, so we wait until LUSERS
            # shows the connection to the previous server
            settle(server.irc_session, ircop_client,
                   lambda: server_link_count(server.irc_session, ircop_client) >= 1)

        server_a, server_c, server_d = servers[0], servers[2], servers[3]

        # Client that pretends to be server D
        d_client = server_c.irc_session.get_client()
        d_client.send_cmd("PASS {} 0210 chirc|test".format(server_c.passwd))
        server_c.irc_session.get_reply(d_client, expect_timeout=True)
        d_client.send_cmd("SERVER {} 1 1 :Test".format(server_d.servername))
        server_c.irc_session.verify_server_registration(d_client, server_c, server_d)

        server_a.irc_session.connect_user("user1", "User One")

        server_c.irc_session.verify_relayed_network_nick(d_client,
                                                         from_server=server_a,
                                                         expect_nick="user1",
                                                         expect_hopcount="3",
                                                         expect_username="user1",
                                                         expect_servertoken=None,
                                                         expect_mode="+",
                                                         expect_fullname="User One")

    def test_chain_list(self, irc_network_session):
        """
        A user on A joins a channel. Checks that a user on D sees that channel
        in LIST (which requires the JOIN to be relayed through B and C).
        """

        servers = create_chain_network(irc_network_session)
        (nick_a, client_a), (nick_d, client_d) = self._connect_end_users(servers)

        client_a.send_cmd("JOIN #test")
        servers[0].irc_session.verify_join(client_a, nick_a, "#test")

        # The JOIN has to be relayed through B and C, so we may have to retry
        servers[3].irc_session.verify_list_eventually({"#test": (nick_a,)}, client_d, nick_d)

    def test_chain_channel(self, irc_network_session):
        """
        A user on A and a user on D join the same channel. Checks that each of
        them sees the other one's messages to the channel (and that the user on
        A sees the user on D join the channel).
        """

        servers = create_chain_network(irc_network_session)
        (nick_a, client_a), (nick_d, client_d) = self._connect_end_users(servers)
        session_a = servers[0].irc_session
        session_d = servers[3].irc_session

        client_a.send_cmd("JOIN #test")
        session_a.verify_join(client_a, nick_a, "#test")

        # Wait until the JOIN has been relayed to D (through B and C)
        settle(session_d, client_d, lambda: channel_known(session_d, client_d, "#test"))

        client_d.send_cmd("JOIN #test")
        session_d.verify_join(client_d, nick_d, "#test")
        session_a.verify_relayed_join(client_a, from_nick=nick_d, channel="#test")

        client_a.send_cmd("PRIVMSG #test :Hello from A")
        session_d.verify_relayed_privmsg(client_d, from_nick=nick_a, recip="#test", msg="Hello from A")

        client_d.send_cmd("PRIVMSG #test :Hello from D")
        session_a.verify_relayed_privmsg(client_a, from_nick=nick_d, recip="#test", msg="Hello from D")

import chirc.replies as replies
import pytest

from chirc.tests.common.fixtures import create_dummy_two_server_network, create_two_server_network
from chirc.types import ReplyTimeoutException


@pytest.mark.category("NETWORK_STATE_WHOIS")
class TestNetworkStateWHOIS(object):

    def test_network_whois1(self, irc_network_session):
        """
        Check that a client doing a WHOIS on themselves shows the
        correct server (the one they're connected to)
        """

        rv = create_two_server_network(irc_network_session,
                                       num_clients_to_passive=1,
                                       num_clients_to_active=1)

        passive_server, active_server, clients_to_passive, clients_to_active = rv

        nick1, client1 = clients_to_passive[0]
        nick101, client101 = clients_to_active[0]

        client1.send_cmd("WHOIS {}".format(nick1))

        reply = passive_server.irc_session.get_reply(client1, expect_code = replies.RPL_WHOISUSER,
                                                     expect_nparams = 5, long_param_re = "User {}".format(nick1))

        expect_short_params = [nick1, passive_server.servername]
        reply = passive_server.irc_session.get_reply(client1, expect_code = replies.RPL_WHOISSERVER,
                                                     expect_short_params=expect_short_params, expect_nparams = 3)

        reply = passive_server.irc_session.get_reply(client1, expect_code = replies.RPL_ENDOFWHOIS,
                                                     expect_nparams = 2, long_param_re = "End of WHOIS list")


    def test_network_whois2(self, irc_network_session):
        """
        Check that a client connected to one server can do a WHOIS of a user
        connected to a different server (and that the correct server is included in RPL_WHOISSERVER)

        In this test, the client doing the WHOIS is connected to the passive server.
        """

        rv = create_two_server_network(irc_network_session,
                                       num_clients_to_passive=1,
                                       num_clients_to_active=1)

        passive_server, active_server, clients_to_passive, clients_to_active = rv

        nick1, client1 = clients_to_passive[0]
        nick101, client101 = clients_to_active[0]

        client1.send_cmd("WHOIS {}".format(nick101))

        reply = passive_server.irc_session.get_reply(client1, expect_code = replies.RPL_WHOISUSER,
                                                     expect_nparams = 5, long_param_re = "User {}".format(nick101))

        expect_short_params = [nick101, active_server.servername]
        reply = passive_server.irc_session.get_reply(client1, expect_code = replies.RPL_WHOISSERVER,
                                                     expect_short_params=expect_short_params, expect_nparams = 3)

        reply = passive_server.irc_session.get_reply(client1, expect_code = replies.RPL_ENDOFWHOIS,
                                                     expect_nparams = 2, long_param_re = "End of WHOIS list")


    def test_network_whois3(self, irc_network_session):
        """
        Check that a client connected to one server can do a WHOIS of a user
        connected to a different server (and that the correct server is included in RPL_WHOISSERVER)

        In this test, the client doing the WHOIS is connected to the active server.
        """

        rv = create_two_server_network(irc_network_session,
                                       num_clients_to_passive=1,
                                       num_clients_to_active=1)

        passive_server, active_server, clients_to_passive, clients_to_active = rv

        nick1, client1 = clients_to_passive[0]
        nick101, client101 = clients_to_active[0]

        client101.send_cmd("WHOIS {}".format(nick1))

        reply = passive_server.irc_session.get_reply(client101, expect_code = replies.RPL_WHOISUSER,
                                                     expect_nparams = 5, long_param_re = "User {}".format(nick1))

        expect_short_params = [nick1, passive_server.servername]
        reply = passive_server.irc_session.get_reply(client101, expect_code = replies.RPL_WHOISSERVER,
                                                     expect_short_params=expect_short_params, expect_nparams = 3)

        reply = passive_server.irc_session.get_reply(client101, expect_code = replies.RPL_ENDOFWHOIS,
                                                     expect_nparams = 2, long_param_re = "End of WHOIS list")


@pytest.mark.category("NETWORK_STATE_LUSERS")
class TestNetworkStateLUSERS(object):

    def test_network_lusers1(self, irc_network_session):
        """
        Check LUSERS with two servers, one client per server, and no channels.
        """

        rv = create_two_server_network(irc_network_session,
                                       num_clients_to_passive=1,
                                       num_clients_to_active=1)

        passive_server, active_server, clients_to_passive, clients_to_active = rv

        nick1, client1 = clients_to_passive[0]

        client1.send_cmd("LUSERS")
        passive_server.irc_session.verify_lusers(client1, nick1,
                                                          expect_users = 2,
                                                          expect_servers = 2,
                                                          expect_ops = 0,
                                                          expect_unknown = 0,
                                                          expect_channels = 0,
                                                          expect_clients = 1,
                                                          expect_direct_servers=1)


    def test_network_lusers2(self, irc_network_session):
        """
        Check LUSERS with two servers, a different number of clients per server, and no channels.
        """

        rv = create_two_server_network(irc_network_session,
                                       num_clients_to_passive=3,
                                       num_clients_to_active=2,
                                       quit_ircop=True)

        passive_server, active_server, clients_to_passive, clients_to_active = rv

        nick1, client1 = clients_to_passive[0]
        nick101, client101 = clients_to_active[0]

        client1.send_cmd("LUSERS")
        passive_server.irc_session.verify_lusers(client1, nick1,
                                                 expect_users = 5,
                                                 expect_servers = 2,
                                                 expect_unknown = 0,
                                                 expect_channels = 0,
                                                 expect_clients = 3,
                                                 expect_direct_servers=1)

        client101.send_cmd("LUSERS")
        active_server.irc_session.verify_lusers(client101, nick101,
                                                 expect_users = 5,
                                                 expect_servers = 2,
                                                 expect_unknown = 0,
                                                 expect_channels = 0,
                                                 expect_clients = 2,
                                                 expect_direct_servers=1)

    def test_network_lusers3(self, irc_network_session):
        """
        Check LUSERS with two servers, a different number of clients per server, and
        channels on just one server.
        """

        rv = create_two_server_network(irc_network_session,
                                       num_clients_to_passive=3,
                                       num_clients_to_active=2,
                                       quit_ircop=True)

        passive_server, active_server, clients_to_passive, clients_to_active = rv

        nick1, client1 = clients_to_passive[0]
        nick2, client2 = clients_to_passive[1]
        nick101, client101 = clients_to_active[0]

        client1.send_cmd("JOIN #test1")
        passive_server.irc_session.verify_join(client1, nick1, "#test1")

        client2.send_cmd("JOIN #test2")
        passive_server.irc_session.verify_join(client2, nick2, "#test2")

        client1.send_cmd("LUSERS")
        passive_server.irc_session.verify_lusers(client1, nick1,
                                                 expect_users = 5,
                                                 expect_servers = 2,
                                                 expect_unknown = 0,
                                                 expect_channels = 2,
                                                 expect_clients = 3,
                                                 expect_direct_servers=1)

        client101.send_cmd("LUSERS")
        active_server.irc_session.verify_lusers(client101, nick101,
                                                 expect_users = 5,
                                                 expect_servers = 2,
                                                 expect_unknown = 0,
                                                 expect_channels = 2,
                                                 expect_clients = 2,
                                                 expect_direct_servers=1)


    def test_network_lusers4(self, irc_network_session):
        """
        Check LUSERS with two servers, a different number of clients per server, and
        channels on both servers (but where the channel names joined on each server are different)
        """

        rv = create_two_server_network(irc_network_session,
                                       num_clients_to_passive=3,
                                       num_clients_to_active=2,
                                       quit_ircop=True)

        passive_server, active_server, clients_to_passive, clients_to_active = rv

        nick1, client1 = clients_to_passive[0]
        nick2, client2 = clients_to_passive[1]
        nick101, client101 = clients_to_active[0]
        nick102, client102 = clients_to_active[1]

        client1.send_cmd("JOIN #test1")
        passive_server.irc_session.verify_join(client1, nick1, "#test1")

        client2.send_cmd("JOIN #test2")
        passive_server.irc_session.verify_join(client2, nick2, "#test2")

        client101.send_cmd("JOIN #test101")
        active_server.irc_session.verify_join(client101, nick101, "#test101")

        client102.send_cmd("JOIN #test102")
        active_server.irc_session.verify_join(client102, nick102, "#test102")

        client1.send_cmd("LUSERS")
        passive_server.irc_session.verify_lusers(client1, nick1,
                                                 expect_users = 5,
                                                 expect_servers = 2,
                                                 expect_unknown = 0,
                                                 expect_channels = 4,
                                                 expect_clients = 3,
                                                 expect_direct_servers=1)

        client101.send_cmd("LUSERS")
        active_server.irc_session.verify_lusers(client101, nick101,
                                                 expect_users = 5,
                                                 expect_servers = 2,
                                                 expect_unknown = 0,
                                                 expect_channels = 4,
                                                 expect_clients = 2,
                                                 expect_direct_servers=1)


    def test_network_lusers5(self, irc_network_session):
        """
        Check LUSERS with two servers, a different number of clients per server, and
        channels on both servers (and where users join channels that may have originated
        in a different server)
        """

        rv = create_two_server_network(irc_network_session,
                                       num_clients_to_passive=3,
                                       num_clients_to_active=2,
                                       quit_ircop=True)

        passive_server, active_server, clients_to_passive, clients_to_active = rv

        nick1, client1 = clients_to_passive[0]
        nick2, client2 = clients_to_passive[1]
        nick101, client101 = clients_to_active[0]
        nick102, client102 = clients_to_active[1]

        client1.send_cmd("JOIN #test1")
        passive_server.irc_session.verify_join(client1, nick1, "#test1")

        client2.send_cmd("JOIN #test2")
        passive_server.irc_session.verify_join(client2, nick2, "#test2")

        client101.send_cmd("JOIN #test101")
        active_server.irc_session.verify_join(client101, nick101, "#test101")

        client102.send_cmd("JOIN #test1")
        active_server.irc_session.verify_join(client102, nick102, "#test1")
        passive_server.irc_session.verify_relayed_join(client1, nick102, "#test1")


        client1.send_cmd("LUSERS")
        passive_server.irc_session.verify_lusers(client1, nick1,
                                                 expect_users = 5,
                                                 expect_servers = 2,
                                                 expect_unknown = 0,
                                                 expect_channels = 3,
                                                 expect_clients = 3,
                                                 expect_direct_servers=1)

        client101.send_cmd("LUSERS")
        active_server.irc_session.verify_lusers(client101, nick101,
                                                 expect_users = 5,
                                                 expect_servers = 2,
                                                 expect_unknown = 0,
                                                 expect_channels = 3,
                                                 expect_clients = 2,
                                                 expect_direct_servers=1)


@pytest.mark.category("NETWORK_STATE_LIST")
class TestNetworkStateLIST(object):

    def test_network_list1(self, irc_network_session):
        """
        Check LIST with two servers and channels on just one server.
        """

        rv = create_two_server_network(irc_network_session,
                                       num_clients_to_passive=3,
                                       num_clients_to_active=2,
                                       quit_ircop=True)

        passive_server, active_server, clients_to_passive, clients_to_active = rv

        nick1, client1 = clients_to_passive[0]
        nick2, client2 = clients_to_passive[1]
        nick101, client101 = clients_to_active[0]

        client1.send_cmd("JOIN #test1")
        passive_server.irc_session.verify_join(client1, nick1, "#test1")

        client2.send_cmd("JOIN #test2")
        passive_server.irc_session.verify_join(client2, nick2, "#test2")

        channels = {"#test1": [nick1],
                    "#test2": [nick2]}

        passive_server.irc_session.verify_list(channels, client1, nick1)


    def test_network_list2(self, irc_network_session):
        """
        Check LIST with two servers and channels on both servers (but where the channel names
        joined on each server are different)
        """

        rv = create_two_server_network(irc_network_session,
                                       num_clients_to_passive=3,
                                       num_clients_to_active=2,
                                       quit_ircop=True)

        passive_server, active_server, clients_to_passive, clients_to_active = rv

        nick1, client1 = clients_to_passive[0]
        nick2, client2 = clients_to_passive[1]
        nick101, client101 = clients_to_active[0]
        nick102, client102 = clients_to_active[1]

        client1.send_cmd("JOIN #test1")
        passive_server.irc_session.verify_join(client1, nick1, "#test1")

        client2.send_cmd("JOIN #test2")
        passive_server.irc_session.verify_join(client2, nick2, "#test2")

        client101.send_cmd("JOIN #test101")
        active_server.irc_session.verify_join(client101, nick101, "#test101")

        client102.send_cmd("JOIN #test102")
        active_server.irc_session.verify_join(client102, nick102, "#test102")

        channels = {"#test1": [nick1],
                    "#test2": [nick2],
                    "#test101": [nick101],
                    "#test102": [nick102]}

        passive_server.irc_session.verify_list(channels, client1, nick1)

        active_server.irc_session.verify_list(channels, client101, nick101)



    def test_network_list3(self, irc_network_session):
        """
        Check LIST with two servers and channels on both servers (and where users
        join channels that may have originated in a different server)
        """

        rv = create_two_server_network(irc_network_session,
                                       num_clients_to_passive=3,
                                       num_clients_to_active=2,
                                       quit_ircop=True)

        passive_server, active_server, clients_to_passive, clients_to_active = rv

        nick1, client1 = clients_to_passive[0]
        nick2, client2 = clients_to_passive[1]
        nick101, client101 = clients_to_active[0]
        nick102, client102 = clients_to_active[1]

        client1.send_cmd("JOIN #test1")
        passive_server.irc_session.verify_join(client1, nick1, "#test1")

        client2.send_cmd("JOIN #test2")
        passive_server.irc_session.verify_join(client2, nick2, "#test2")

        client101.send_cmd("JOIN #test101")
        active_server.irc_session.verify_join(client101, nick101, "#test101")

        client102.send_cmd("JOIN #test1")
        active_server.irc_session.verify_join(client102, nick102, "#test1")
        passive_server.irc_session.verify_relayed_join(client1, nick102, "#test1")

        channels = {"#test1": [nick1, nick102],
                    "#test2": [nick2],
                    "#test101": [nick101]}

        passive_server.irc_session.verify_list(channels, client1, nick1)

        active_server.irc_session.verify_list(channels, client101, nick101)

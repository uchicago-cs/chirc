from chirc import replies
from chirc.tests.common.sessions import wait_for
import re


#
# Best-effort waits for relayed messages
#
# These use read-only queries (LUSERS, WHOIS, LIST) to check whether
# messages relayed between servers have arrived. They never fail a test by
# themselves: if the condition isn't met before the deadline, the test just
# carries on (and the test's own checks will then fail, if appropriate).
# The client used for the query must not be expecting other messages at
# that point (otherwise, the query could read them instead).
#

def server_link_count(irc_session, client):
    """Returns the number of directly connected servers reported by LUSERS (or -1)"""
    msgs = irc_session.query(client, "LUSERS", {replies.RPL_LUSERME})
    if msgs is None:
        return -1
    match = re.search(r"and (\d+) servers", msgs[-1].params[-1])
    return int(match.group(1)) if match else -1

def nick_known(irc_session, client, nick):
    """Returns True if a WHOIS for `nick` succeeds"""
    msgs = irc_session.query(client, "WHOIS {}".format(nick), {replies.RPL_ENDOFWHOIS, replies.ERR_NOSUCHNICK})
    return msgs is not None and any(m.cmd == replies.RPL_WHOISUSER for m in msgs)

def channel_known(irc_session, client, channel):
    """Returns True if LIST includes `channel`"""
    msgs = irc_session.query(client, "LIST", {replies.RPL_LISTEND})
    return msgs is not None and any(m.cmd == replies.RPL_LIST and m.params[1] == channel for m in msgs)

def settle(irc_session, client, condition):
    """Waits (best-effort) until `condition()` is True. If it never becomes True,
    we discard any late replies to the queries, so they don't surprise the rest
    of the test (if it does become True, the last query read all its replies).

    Once a wait has timed out in a test, the network is unlikely to settle
    (e.g., because CONNECT isn't implemented yet), so any later waits in the
    same test only check the condition once, instead of waiting again.
    """
    gave_up = getattr(irc_session, "network_gave_up", False)
    if wait_for(condition, timeout = 0 if gave_up else irc_session.RELAY_TIMEOUT):
        return

    irc_session.drain(client)

    # Remember that we gave up, in every server of this network
    if irc_session.irc_network is not None:
        for server in irc_session.irc_network:
            server.irc_session.network_gave_up = True
    else:
        irc_session.network_gave_up = True

channels1 = { "#test1": ("@user1", "user2", "user3"),
              "#test2": ("@user4", "user5", "user6"),
              "#test3": ("@user7", "user8", "user9")
            }

channels2 = { "#test1": ("@user1", "user2", "user3"),
              "#test2": ("@user4", "user5", "user6"),
              "#test3": ("@user7", "user8", "user9"),
                  None: ("user10" , "user11")
            }
                
channels3 = { "#test1": ("@user1", "user2", "user3"),
              "#test2": ("@user2",),
              "#test3": ("@user3", "@user4", "user5", "user6"),
              "#test4": ("@user7", "+user8", "+user9", "user1", "user2"),
              "#test5": ("@user1", "@user5"),
                  None: ("user10" , "user11")
            }                
                
channels4 = { None: ("user1", "user2", "user3", "user4", "user5") }

def create_dummy_two_server_network(irc_network_session, num_clients_to_passive=0, num_dummy_users_in_active=0):
    """
    Creates a two-server network, but one where only the passive
    server is actually running. We simulate the active server
    with a client, to check whether the passive server produces
    the correct replies, relays, etc.
    """
    irc_network_session.set_servers(2)
    irc_network_session.start_session(0)
    passive_server = irc_network_session.servers[0]
    active_server = irc_network_session.servers[1]

    irc_session = passive_server.irc_session
    active_client = irc_session.get_client()

    active_client.send_cmd("PASS {} 0210 chirc|test".format(passive_server.passwd))
    irc_session.get_reply(active_client, expect_timeout=True)

    active_client.send_cmd("SERVER {} 1 1 :Test".format(active_server.servername))

    irc_session.verify_server_registration(active_client, passive_server, active_server)

    clients_to_passive = []
    for i in range(num_clients_to_passive):
        nick = "user%i" % (i+1)
        username = "User %s" % nick
        client =  irc_session.connect_user(nick, username)
        clients_to_passive.append( (nick, client) )

        irc_session.verify_relayed_network_nick(active_client,
                                                from_server=passive_server,
                                                expect_nick=nick,
                                                expect_hopcount="1",
                                                expect_username=nick,
                                                expect_servertoken=None,
                                                expect_mode="+",
                                                expect_fullname=username)

    dummy_active_nicks = []
    for i in range(num_dummy_users_in_active):
        nick = "user%i" % (i+101)
        username = "User %s" % nick
        dummy_active_nicks.append(nick)

        cmd = ":{} NICK {} 1 {} 127.0.0.1 1 + :{}"
        cmd = cmd.format(active_server.servername, nick, nick, username)

        active_client.send_cmd(cmd)
        irc_session.get_reply(active_client, expect_timeout=True)


    return passive_server, active_server, active_client, clients_to_passive, dummy_active_nicks


def create_two_server_network(irc_network_session, num_clients_to_passive=0, num_clients_to_active=0, quit_ircop=False):
    irc_network_session.set_servers(2)
    irc_network_session.start_sessions()

    passive_server = irc_network_session.servers[0]
    active_server = irc_network_session.servers[1]

    ircop_client = active_server.irc_session.connect_user("ircop", "IRC Operator")

    ircop_client.send_cmd("OPER ircop {}".format(active_server.irc_session.oper_password))

    reply = active_server.irc_session.get_reply(ircop_client, expect_code = replies.RPL_YOUREOPER,
                                                expect_nick = "ircop",
                                                expect_nparams = 1,
                                                long_param_re = "You are now an IRC operator")

    # We send 0 as the port, since the port must be taken from the network specification file
    ircop_client.send_cmd("CONNECT {} 0".format(passive_server.servername))

    # CONNECT doesn't return anything on success, so we wait until LUSERS
    # shows the connection to the other server
    settle(active_server.irc_session, ircop_client,
           lambda: server_link_count(active_server.irc_session, ircop_client) >= 1)

    if quit_ircop:
        ircop_client.send_cmd("QUIT")
        active_server.irc_session.get_message(ircop_client, expect_cmd = "ERROR", expect_nparams = 1)

    clients_to_passive = []
    for i in range(num_clients_to_passive):
        nick = "user%i" % (i+1)
        username = "User %s" % nick
        client =  passive_server.irc_session.connect_user(nick, username)
        clients_to_passive.append( (nick, client) )

    clients_to_active = []
    for i in range(num_clients_to_active):
        nick = "user%i" % (i+101)
        username = "User %s" % nick
        client =  active_server.irc_session.connect_user(nick, username)
        clients_to_active.append( (nick, client) )

    # Wait until each server knows about the users connected to the other one.
    # NICKs are relayed in order, so it's enough to check for the last one.
    if clients_to_passive and clients_to_active:
        last_passive_nick = clients_to_passive[-1][0]
        last_active_nick = clients_to_active[-1][0]
        _, active_client = clients_to_active[0]
        _, passive_client = clients_to_passive[0]
        settle(active_server.irc_session, active_client,
               lambda: nick_known(active_server.irc_session, active_client, last_passive_nick))
        settle(passive_server.irc_session, passive_client,
               lambda: nick_known(passive_server.irc_session, passive_client, last_active_nick))
    elif clients_to_passive and not quit_ircop:
        last_passive_nick = clients_to_passive[-1][0]
        settle(active_server.irc_session, ircop_client,
               lambda: nick_known(active_server.irc_session, ircop_client, last_passive_nick))

    return passive_server, active_server, clients_to_passive, clients_to_active


def create_dummy_hub_network(irc_network_session, num_clients_to_hub=0):
    """
    Creates a four-server hub-and-spoke network (A-B, A-C, A-D), but one
    where only the hub (A) is actually running. We simulate the three
    spoke servers (B, C, D) with clients, to check whether the hub
    produces the correct replies, relays, etc.
    """
    irc_network_session.set_servers(4)
    irc_network_session.start_session(0)
    hub_server = irc_network_session.servers[0]
    spoke_servers = irc_network_session.servers[1:]

    irc_session = hub_server.irc_session

    spoke_clients = []
    for spoke_server in spoke_servers:
        spoke_client = irc_session.get_client()

        spoke_client.send_cmd("PASS {} 0210 chirc|test".format(hub_server.passwd))
        irc_session.get_reply(spoke_client, expect_timeout=True)

        spoke_client.send_cmd("SERVER {} 1 1 :Test".format(spoke_server.servername))

        irc_session.verify_server_registration(spoke_client, hub_server, spoke_server)

        spoke_clients.append(spoke_client)

    clients_to_hub = []
    for i in range(num_clients_to_hub):
        nick = "user%i" % (i+1)
        username = "User %s" % nick
        client = irc_session.connect_user(nick, username)
        clients_to_hub.append( (nick, client) )

        # The NICK should be relayed to every spoke server
        for spoke_client in spoke_clients:
            irc_session.verify_relayed_network_nick(spoke_client,
                                                    from_server=hub_server,
                                                    expect_nick=nick,
                                                    expect_hopcount="1",
                                                    expect_username=nick,
                                                    expect_servertoken=None,
                                                    expect_mode="+",
                                                    expect_fullname=username)

    return hub_server, spoke_servers, spoke_clients, clients_to_hub


def create_hub_network(irc_network_session, num_clients_to_hub=0):
    """
    Creates a four-server hub-and-spoke network (A-B, A-C, A-D) with all
    four servers running. Each spoke server (B, C, D) connects to the
    hub (A) by having an IRC operator on the spoke send a CONNECT command.
    """
    irc_network_session.set_servers(4)
    irc_network_session.start_sessions()

    hub_server = irc_network_session.servers[0]
    spoke_servers = irc_network_session.servers[1:]

    ircop_clients = []
    for i, spoke_server in enumerate(spoke_servers):
        nick = "ircop%i" % (i+2)
        ircop_client = spoke_server.irc_session.connect_user(nick, "IRC Operator")

        ircop_client.send_cmd("OPER {} {}".format(nick, spoke_server.irc_session.oper_password))

        spoke_server.irc_session.get_reply(ircop_client, expect_code = replies.RPL_YOUREOPER,
                                           expect_nick = nick,
                                           expect_nparams = 1,
                                           long_param_re = "You are now an IRC operator")

        # We send 0 as the port, since the port must be taken from the network specification file
        ircop_client.send_cmd("CONNECT {} 0".format(hub_server.servername))

        ircop_clients.append( (nick, ircop_client) )

    # CONNECT doesn't return anything on success, so we wait until LUSERS
    # on each spoke shows its connection to the hub
    for spoke_server, (nick, ircop_client) in zip(spoke_servers, ircop_clients):
        settle(spoke_server.irc_session, ircop_client,
               lambda: server_link_count(spoke_server.irc_session, ircop_client) >= 1)

    clients_to_hub = []
    for i in range(num_clients_to_hub):
        nick = "user%i" % (i+1)
        username = "User %s" % nick
        client = hub_server.irc_session.connect_user(nick, username)
        clients_to_hub.append( (nick, client) )

    # Wait until every spoke knows about the users connected to the hub
    # (NICKs are relayed in order, so it's enough to check for the last one)
    if clients_to_hub:
        last_nick = clients_to_hub[-1][0]
        for spoke_server, (nick, ircop_client) in zip(spoke_servers, ircop_clients):
            settle(spoke_server.irc_session, ircop_client,
                   lambda: nick_known(spoke_server.irc_session, ircop_client, last_nick))

    return hub_server, spoke_servers, ircop_clients, clients_to_hub


def create_chain_network(irc_network_session):
    """
    Creates a four-server network where the servers are connected
    in sequence (A-B-C-D). Each server (except A) connects to the
    previous one by having an IRC operator send a CONNECT command
    (B connects to A, C connects to B, and D connects to C).
    """
    irc_network_session.set_servers(4)
    irc_network_session.start_sessions()

    servers = irc_network_session.servers

    for i in range(1, len(servers)):
        server = servers[i]
        prev_server = servers[i-1]

        nick = "ircop%i" % (i+1)
        ircop_client = server.irc_session.connect_user(nick, "IRC Operator")

        ircop_client.send_cmd("OPER {} {}".format(nick, server.irc_session.oper_password))

        server.irc_session.get_reply(ircop_client, expect_code = replies.RPL_YOUREOPER,
                                     expect_nick = nick,
                                     expect_nparams = 1,
                                     long_param_re = "You are now an IRC operator")

        # We send 0 as the port, since the port must be taken from the network specification file
        ircop_client.send_cmd("CONNECT {} 0".format(prev_server.servername))

        # CONNECT doesn't return anything on success, so we wait until LUSERS
        # shows the connection to the previous server
        settle(server.irc_session, ircop_client,
               lambda: server_link_count(server.irc_session, ircop_client) >= 1)

    return servers

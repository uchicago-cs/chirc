from chirc import replies
import time

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
    irc_network_session.start_session(0)
    irc_network_session.start_session(1)

    passive_server = irc_network_session.servers[0]
    active_server = irc_network_session.servers[1]

    ircop_client = active_server.irc_session.connect_user("ircop", "IRC Operator")

    ircop_client.send_cmd("OPER ircop {}".format(active_server.irc_session.oper_password))

    reply = active_server.irc_session.get_reply(ircop_client, expect_code = replies.RPL_YOUREOPER,
                                                expect_nick = "ircop",
                                                expect_nparams = 1,
                                                long_param_re = "You are now an IRC operator")

    ircop_client.send_cmd("CONNECT {} {}".format(passive_server.servername, passive_server.port))

    if quit_ircop:
        ircop_client.send_cmd("QUIT")
        active_server.irc_session.get_message(ircop_client, expect_cmd = "ERROR", expect_nparams = 1)

    # Since CONNECT doesn't return anything on success, we need to add an arbitrary delay
    # to make sure it's had time to complete
    time.sleep(0.1)

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

    # Since we have no way to check whether the NICK relays were all completed, we
    # need to use an arbitrary delay
    time.sleep(0.1)

    return passive_server, active_server, clients_to_passive, clients_to_active

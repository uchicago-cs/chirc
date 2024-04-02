import pytest
from chirc.tests.common.fixtures import channels1, channels2, channels3
from chirc import replies

class BaseTestPermissions(object):
    """Base class for permission tests"""

    def _join_and_mode(self, irc_session, numclients, channel, mode):
        """
        Have `numclients` connect to the server, and have them all join
        the `channel` channel. The first user to join the channel (who
        should get operator privileges) sets the channel mode to `mode`
        and we check that everyone received the relay of the MODE.
        """

        clients = irc_session.connect_clients(numclients, join_channel = channel)

        nick1, client1 = clients[0]

        irc_session.set_channel_mode(client1, nick1, channel, mode)

        for nick, client in clients:
            irc_session.verify_relayed_mode(client, from_nick=nick1, channel=channel, mode=mode)

        return clients

    def _privmsg(self, irc_session, client, nick, channel, clients):
        """
        User `nick` sends a message to channel `channel` and we check
        that everyone received the relay of the message
        """

        client.send_cmd("PRIVMSG %s :Hello from %s!" % (channel,nick))
        for (nick2, client2) in clients:
            if nick != nick2:
                irc_session.verify_relayed_privmsg(client2, from_nick=nick, recip=channel, msg="Hello from %s!" % nick)

    def _oper(self, irc_session, client, nick):
        """
        Gives user `nick` IRCop privileges
        """

        client.send_cmd("OPER %s %s" % (nick, irc_session.oper_password))

        reply = irc_session.get_reply(client, expect_code = replies.RPL_YOUREOPER, expect_nick = nick,
                                      expect_nparams = 1,
                                      long_param_re = "You are now an IRC operator")


@pytest.mark.category("BASIC_MODE")
class TestBasicMODE(object):

    def test_mode_params(self, irc_session):
        """
        Test ERR_NEEDMOREPARAMS reply
        """

        client1 = irc_session.connect_user("user1", "User One")

        client1.send_cmd("MODE")

        irc_session.get_ERR_NEEDMOREPARAMS_reply(client1,
                                                 expect_nick="user1", expect_cmd="MODE")

    def test_channel_membership_errors01(self, irc_session):
        """
        A user tries to set another user's member status mode (in #test)
        to +o. The user exists but the channel does not."""

        client1 = irc_session.connect_user("user1", "User One")
        _ = irc_session.connect_user("user2", "User Two")

        irc_session.set_channel_mode(client1, "user1", "#test", "+o", "user2", expect_wrong_channel = True)

    def test_channel_membership_errors02(self, irc_session):
        """
        A user tries to set another user's member status mode (in #test)
        to +o. Neither the user nor the channel exist."""

        client1 = irc_session.connect_user("user1", "User One")

        irc_session.set_channel_mode(client1, "user1", "#test", "+v", "user2", expect_wrong_channel = True)

    def test_channel_membership_errors03(self, irc_session):
        """
        Two users connect to the server and they both join the #test channel.

        The first user tries to set the member status mode of a user that
        is not in the server.
        """

        clients = irc_session.connect_clients(2, join_channel = "#test")

        nick1, client1 = clients[0]
        nick2, client2 = clients[1]

        irc_session.set_channel_mode(client1, nick1, "#test", "+o", "user3", expect_not_on_channel = True)


    def test_channel_membership_errors04(self, irc_session):
        """
        Two users connect to the server and the first one joins the #test channel.

        The first user tries to set the member status mode of the second user
        (who is not in the channel)
        """

        client1 = irc_session.connect_user("user1", "User One")

        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, "user1", "#test")

        client2 = irc_session.connect_user("user2", "User Two")

        irc_session.set_channel_mode(client1, "user1", "#test", "+o", "user2", expect_not_on_channel = True)

    def test_channel_membership_errors05(self, irc_session):
        """
        Two users connect to the server and they both join the #test channel.

        The first user tries to set the second user's member status mode to
        a mode that is not valid.
        """

        clients = irc_session.connect_clients(2, join_channel = "#test")

        nick1, client1 = clients[0]
        nick2, client2 = clients[1]

        irc_session.set_channel_mode(client1, nick1, "#test", "+z", "user2", expect_wrong_mode = True)


@pytest.mark.category("BASIC_CHANNEL_OPERATOR")
class TestChannelOperator(object):
    """
    Basic tests for channel operator functionality (for Assignment 2.5)
    """

    def test_channel_operator01(self, irc_session):
        """
        Connects three users to the server, and has them join
        channel #test. Checks that the first user (user1) is
        granted operator privileges (by checking the NAMES
        returned when joining the channel)
        """
        irc_session.connect_and_join_channels({"#test": ("@user1", "user2", "user3")})

    def test_channel_operator02(self, irc_session):
        """
        Connects nine users to the server, and has them join
        the following channels. Checks that the first user to
        join is granted operator privileges.

        #test1: @user1, user2, user3
        #test2: @user4, user5, user6
        #test3: @user7, user8, user9
        """
        irc_session.connect_and_join_channels(channels1)

    def test_channel_operator03(self, irc_session):
        """
        Connects elevel users to the server, and has nine of them join
        the following channels. Checks that the first user to
        join is granted operator privileges.

        #test1: @user1, user2, user3
        #test2: @user4, user5, user6
        #test3: @user7, user8, user9

        Not in a channel: user10, user11
        """
        irc_session.connect_and_join_channels(channels2)

    def test_channel_operator04(self, irc_session):
        """
        Ten users connect to the server and they all join the #test channel.

        The first user to join the channel (the operator) gives operator
        privileges to user2 (+o)

        We check that everyone in the channel receives the relay of the MODE
        """

        clients = irc_session.connect_clients(10, join_channel = "#test")

        nick1, client1 = clients[0]

        irc_session.set_channel_mode(client1, nick1, "#test", "+o", "user2")

        for nick, client in clients:
            irc_session.verify_relayed_mode(client, from_nick=nick1, channel="#test", mode="+o", mode_nick="user2")

    def test_channel_operator05(self, irc_session):
        """
        Ten users connect to the server and they all join the #test channel.

        The second user to join the channel (who should not have operator
        privileges) tries to give operator privileges to user3, but is denied.

        We check that no one in the channel receives a relay of the MODE
        """

        clients = irc_session.connect_clients(10, join_channel = "#test")

        nick2, client2 = clients[1]

        irc_session.set_channel_mode(client2, nick2, "#test", "+o", "user3", expect_ops_needed=True)

        for nick, client in clients:
            irc_session.get_reply(client, expect_timeout = True)

    def test_channel_operator06(self, irc_session):
        """
        Ten users connect to the server and they all join the #test channel.

        The second user to join the channel (who should not have operator
        privileges) tries to take operator privileges away from the operator,
        but is denied.

        We check that no one in the channel receives a relay of the MODE
        """

        clients = irc_session.connect_clients(10, join_channel = "#test")

        nick2, client2 = clients[1]

        irc_session.set_channel_mode(client2, nick2, "#test", "-o", "user1", expect_ops_needed=True)

        for nick, client in clients:
            irc_session.get_reply(client, expect_timeout = True)


    def test_channel_operator07(self, irc_session):
        """
        Ten users connect to the server and they all join the #test channel.

        The following happens:

        - user1 gives user2 operator privileges in the channel. We check
          that everyone receives the relay.
        - user2 gives user3 operator privileges in the channel. We check
          that everyone receives the relay.
        - user1 takes away the operator privileges from user2. We check
          that everyone receives the relay.
        - user2 (who is no longer an operator) tries to give operator privileges
          to user4, but is denied. We check that no one receives a MODE relay
        """

        clients = irc_session.connect_clients(5, join_channel = "#test")

        nick1, client1 = clients[0]
        nick2, client2 = clients[1]

        irc_session.set_channel_mode(client1, nick1, "#test", "+o", "user2")
        for nick, client in clients:
            irc_session.verify_relayed_mode(client, from_nick=nick1, channel="#test", mode="+o", mode_nick="user2")

        irc_session.set_channel_mode(client2, nick2, "#test", "+o", "user3")
        for nick, client in clients:
            irc_session.verify_relayed_mode(client, from_nick=nick2, channel="#test", mode="+o", mode_nick="user3")

        irc_session.set_channel_mode(client1, nick1, "#test", "-o", "user2")
        for nick, client in clients:
            irc_session.verify_relayed_mode(client, from_nick=nick1, channel="#test", mode="-o", mode_nick="user2")

        irc_session.set_channel_mode(client2, nick2, "#test", "+o", "user4", expect_ops_needed=True)

        for nick, client in clients:
            irc_session.get_reply(client, expect_timeout = True)



@pytest.mark.category("BASIC_IRC_OPERATOR")
class TestOPER(object):

    def test_oper1(self, irc_session):
        """
        Tests giving a user (user1) IRCop privileges.
        """

        client1 = irc_session.connect_user("user1", "User One")

        client1.send_cmd("OPER user1 %s" % irc_session.oper_password)

        reply = irc_session.get_reply(client1, expect_code = replies.RPL_YOUREOPER, expect_nick = "user1",
                                      expect_nparams = 1,
                                      long_param_re = "You are now an IRC operator")

    def test_oper2(self, irc_session):
        """
        Tests giving a user (user1) IRCop privileges, but providing
        an incorrect password.
        """

        client1 = irc_session.connect_user("user1", "User One")

        client1.send_cmd("OPER user1 BAD%s" % irc_session.oper_password)

        reply = irc_session.get_reply(client1, expect_code = replies.ERR_PASSWDMISMATCH, expect_nick = "user1",
                                      expect_nparams = 1,
                                      long_param_re = "Password incorrect")

    def test_oper_params(self, irc_session):
        """
        Test ERR_NEEDMOREPARAMS reply
        """

        client1 = irc_session.connect_user("user1", "User One")

        client1.send_cmd("OPER")

        irc_session.get_ERR_NEEDMOREPARAMS_reply(client1,
                                                 expect_nick="user1", expect_cmd="OPER")


@pytest.mark.category("BASIC_IRC_OPERATOR")
class TestPermissionsOPERBasic(BaseTestPermissions):

    def test_permissions_oper_basic1(self, irc_session):
        """
        Check that an IRCop can grant operator privileges to someone on a channel
        despite not being a channel operator.
        """

        clients = irc_session.connect_clients(3, join_channel = "#test")

        nick2, client2 = clients[1]

        self._oper(irc_session, client2, nick2)

        irc_session.set_channel_mode(client2, nick2, "#test", "+o", "user3")

        for nick, client in clients:
            irc_session.verify_relayed_mode(client, from_nick=nick2, channel="#test", mode="+o", mode_nick="user3")

@pytest.mark.category("MODES")
class TestUserMODE(object):
     
    def test_user_mode01(self, irc_session):
        """
        The user tries to give itself IRCop status using MODE.
        This is not allowed, but there is no error reply. There is simply
        no relay of the MODE
        """
        
        client1 = irc_session.connect_user("user1", "User One")
        
        irc_session.set_user_mode(client1, "user1", "user1", "+o", expect_relay=False)
    
    def test_user_mode02(self, irc_session):
        """
        The user tries to remove IRCop status from itself using MODE
        (and the user is not already an IRCop) A non-IRCop can't
        modify the the 'o' user mode, but since the user isn't
        an IRCop, requesting -o has no effect, and the MODE
        is relayed back (because it is accurate: the user is not
        an IRCop)
        """
                
        client1 = irc_session.connect_user("user1", "User One")
        
        irc_session.set_user_mode(client1, "user1", "user1", "-o")

    def test_user_mode03(self, irc_session):
        """
        The user tries to go away using MODE instead of AWAY.
        This is not allowed, but there is no error reply. 
        There is simply no relay of the MODE
        """
                
        client1 = irc_session.connect_user("user1", "User One")
        
        irc_session.set_user_mode(client1, "user1", "user1", "+a", expect_relay=False)

    def test_user_mode04(self, irc_session):
        """
        The user tries to return from away using MODE instead of AWAY.
        This is not allowed, but there is no error reply. 
        There is simply no relay of the MODE
        """

        client1 = irc_session.connect_user("user1", "User One")
        
        irc_session.set_user_mode(client1, "user1", "user1", "-a", expect_relay=False)
        
    def test_user_mode05(self, irc_session):
        """
        The user tries to set its "v" mode. This is a valid member status mode,
        but not a valid user mode. ERR_UMODEUNKNOWNFLAG should be returned.
        """

        client1 = irc_session.connect_user("user1", "User One")
        
        irc_session.set_user_mode(client1, "user1", "user1", "+v", expect_wrong_mode=True)
        
    def test_user_mode06(self, irc_session):
        """
        The user tries to unset its "v" mode. This is a valid member status mode,
        but not a valid user mode. ERR_UMODEUNKNOWNFLAG should be returned.
        """

        client1 = irc_session.connect_user("user1", "User One")
        
        irc_session.set_user_mode(client1, "user1", "user1", "-v", expect_wrong_mode=True)
        
    def test_user_mode07(self, irc_session):
        """
        The user tries to set its "t" mode. This is a valid channel mode,
        but not a valid user mode. ERR_UMODEUNKNOWNFLAG should be returned.
        """

        client1 = irc_session.connect_user("user1", "User One")
        
        irc_session.set_user_mode(client1, "user1", "user1", "+t", expect_wrong_mode=True)
        
    def test_user_mode08(self, irc_session):
        """
        The user tries to unset its "t" mode. This is a valid channel mode,
        but not a valid user mode. ERR_UMODEUNKNOWNFLAG should be returned.
        """

        client1 = irc_session.connect_user("user1", "User One")
        
        irc_session.set_user_mode(client1, "user1", "user1", "-t", expect_wrong_mode=True)        
        
    def test_user_mode09(self, irc_session):
        """
        The user tries to set its "z" mode. This is not a supported mode
        in chIRC, so ERR_UMODEUNKNOWNFLAG should be returned.
        """
        
        client1 = irc_session.connect_user("user1", "User One")
        
        irc_session.set_user_mode(client1, "user1", "user1", "+z", expect_wrong_mode=True)
        
    def test_user_mode10(self, irc_session):
        """
        The user tries to unset its "z" mode. This is not a supported mode
        in chIRC, so ERR_UMODEUNKNOWNFLAG should be returned.
        """

        client1 = irc_session.connect_user("user1", "User One")
        
        irc_session.set_user_mode(client1, "user1", "user1", "-z", expect_wrong_mode=True)        
        
    def test_user_mode11(self, irc_session):
        """
        The user tries to unset the "o" mode for another user. 
        
        ERR_USERSDONTMATCH should be returned.
        """

        client1 = irc_session.connect_user("user1", "User One")
        
        irc_session.set_user_mode(client1, "user1", "user2", "-o")   

    def test_user_mode12(self, irc_session):
        """
        The user tries to unset the "z" mode for another user. 
        
        ERR_USERSDONTMATCH should be returned (even though "z" is not a valid user mode)
        """

        client1 = irc_session.connect_user("user1", "User One")
        
        irc_session.set_user_mode(client1, "user1", "user2", "-z")


@pytest.mark.category("MODES")
class TestChannelMODE(object):

    def test_channel_mode01(self, irc_session):
        """
        A user joins a channel and sets it to be moderated (+m)
        """
        
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, "user1", "#test")
        
        irc_session.set_channel_mode(client1, "user1", "#test", "+m")
        irc_session.verify_relayed_mode(client1, "user1", "#test", "+m")
        
    def test_channel_mode02(self, irc_session):
        """
        A user joins a channel and sets it so that only the channel
        operator can change the topic (+t)
        """
        
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, "user1", "#test")
        
        irc_session.set_channel_mode(client1, "user1", "#test", "+t")
        irc_session.verify_relayed_mode(client1, "user1", "#test", "+t")        
        
    def test_channel_mode03(self, irc_session):
        """
        A user joins a channel and sets it so it will not be moderated (-m)
        """

        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, "user1", "#test")
        
        irc_session.set_channel_mode(client1, "user1", "#test", "-m")
        irc_session.verify_relayed_mode(client1, "user1", "#test", "-m")
        
    def test_channel_mode04(self, irc_session):
        """
        A user joins a channel and sets it so that anyone in the channel
        can change the topic (+t)
        """
        
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, "user1", "#test")
        
        irc_session.set_channel_mode(client1, "user1", "#test", "-t")
        irc_session.verify_relayed_mode(client1, "user1", "#test", "-t")
        
    def test_channel_mode05(self, irc_session):
        """
        A user joins a channel and tries to set an unsupported channel mode (+z)
        """
                
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, "user1", "#test")
        
        irc_session.set_channel_mode(client1, "user1", "#test", "+z", expect_wrong_mode=True)               
        
    def test_channel_mode06(self, irc_session):
        """
        A user joins a channel and tries to set an unsupported channel mode (+o),
        althought is _is_ a supported member status mode.
        """

        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, "user1", "#test")
        
        irc_session.set_channel_mode(client1, "user1", "#test", "+o", expect_wrong_mode=True)             
        
    def test_channel_mode07(self, irc_session):
        """
        A user joins a channel and tries to set an unsupported channel mode (+v),
        althought is _is_ a supported member status mode.
        """

        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, "user1", "#test")
        
        irc_session.set_channel_mode(client1, "user1", "#test", "+v", expect_wrong_mode=True)        
        
    def test_channel_mode08(self, irc_session):
        """
        A user joins a channel and sets it to be moderated (+m). Then it asks
        for the channel modes, and checks that "m" is one of the modes.
        """
                
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, "user1", "#test")
        
        irc_session.set_channel_mode(client1, "user1", "#test", "+m")
        irc_session.verify_relayed_mode(client1, "user1", "#test", "+m")      
        
        irc_session.set_channel_mode(client1, "user1", "#test", expect_mode = "m")
        
    def test_channel_mode09(self, irc_session):
        """
        A user joins a channel and sets it to be moderated (+m) and so that
        only channel operators can change the topic (+t). Then it asks
        for the channel modes, and checks that "m" and "t" are modes of the channel.
        """

        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, "user1", "#test")
        
        irc_session.set_channel_mode(client1, "user1", "#test", "+m")
        irc_session.verify_relayed_mode(client1, "user1", "#test", "+m")      

        irc_session.set_channel_mode(client1, "user1", "#test", "+t")
        irc_session.verify_relayed_mode(client1, "user1", "#test", "+t")      
        
        irc_session.set_channel_mode(client1, "user1", "#test", expect_mode = "mt")           
        
    def test_channel_mode10(self, irc_session):
        """
        A user joins a channel and sets it to be moderated (+m) and so that
        only channel operators can change the topic (+t), then removes that mode (-t).
        Then it asks for the channel modes, and checks that only "m" is set.
        """
        
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, "user1", "#test")
        
        irc_session.set_channel_mode(client1, "user1", "#test", "+m")
        irc_session.verify_relayed_mode(client1, "user1", "#test", "+m")      

        irc_session.set_channel_mode(client1, "user1", "#test", "+t")
        irc_session.verify_relayed_mode(client1, "user1", "#test", "+t")      

        irc_session.set_channel_mode(client1, "user1", "#test", "-t")
        irc_session.verify_relayed_mode(client1, "user1", "#test", "-t")      
        
        irc_session.set_channel_mode(client1, "user1", "#test", expect_mode = "m")                 
    
    def test_channel_mode11(self, irc_session):
        """
        A user joins a channel and sets it to be moderated (+m) and so that
        only channel operators can change the topic (+t), then makes it unmoderated (-m).
        Then it asks for the channel modes, and checks that only "t" is set.
        """

        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, "user1", "#test")
        
        irc_session.set_channel_mode(client1, "user1", "#test", "+m")
        irc_session.verify_relayed_mode(client1, "user1", "#test", "+m")      

        irc_session.set_channel_mode(client1, "user1", "#test", "+t")
        irc_session.verify_relayed_mode(client1, "user1", "#test", "+t")      

        irc_session.set_channel_mode(client1, "user1", "#test", "-m")
        irc_session.verify_relayed_mode(client1, "user1", "#test", "-m")      
        
        irc_session.set_channel_mode(client1, "user1", "#test", expect_mode = "t")    
        
    def test_channel_mode12(self, irc_session):
        """
        A user joins a channel and sets it to be moderated (+m) and so that
        only channel operators can change the topic (+t), then removes both
        those modes (-m and -t). Then it asks for the channel modes, and 
        checks that no modes are set.
        """
        
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, "user1", "#test")
        
        irc_session.set_channel_mode(client1, "user1", "#test", "+m")
        irc_session.verify_relayed_mode(client1, "user1", "#test", "+m")      

        irc_session.set_channel_mode(client1, "user1", "#test", "+t")
        irc_session.verify_relayed_mode(client1, "user1", "#test", "+t")      

        irc_session.set_channel_mode(client1, "user1", "#test", "-m")
        irc_session.verify_relayed_mode(client1, "user1", "#test", "-m")      

        irc_session.set_channel_mode(client1, "user1", "#test", "-t")
        irc_session.verify_relayed_mode(client1, "user1", "#test", "-t")      
        
        irc_session.set_channel_mode(client1, "user1", "#test", expect_mode = "")         
        

    def test_channel_mode13(self, irc_session):
        """
        A user joins a channel and asks for its modes. There should be none.
        """
        
        client1 = irc_session.connect_user("user1", "User One")
        
        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, "user1", "#test")  
        
        irc_session.set_channel_mode(client1, "user1", "#test", expect_mode = "")       
        

    def test_channel_mode14(self, irc_session):
        """
        A user tries to ask for the modes of a channel that doesn't exist.
        """
        
        client1 = irc_session.connect_user("user1", "User One")
        
        irc_session.set_channel_mode(client1, "user1", "#test", expect_wrong_channel = True)      
        

    def test_channel_mode15(self, irc_session):
        """
        A user tries to set the mode of a channel that doesn't exist.
        """
        
        client1 = irc_session.connect_user("user1", "User One")
        
        irc_session.set_channel_mode(client1, "user1", "#test", "+m", expect_wrong_channel = True)      
        

    def test_channel_mode16(self, irc_session):
        """
        A user tries to set the mode of a channel that doesn't exist.
        The specified mode is also not a valid channel mode (but we
        don't get an error for that)
        """

        client1 = irc_session.connect_user("user1", "User One")
        
        irc_session.set_channel_mode(client1, "user1", "#test", "+o", expect_wrong_channel = True)   
        

    def test_channel_mode17(self, irc_session):
        """
        Ten clients connect to the server, and they all join the same channel.
        
        The first user to join the channel (the operator) sets the channel to be
        moderated.
        
        We check that everyone in the channel receives the relay of the MODE
        """
        
        clients = irc_session.connect_clients(10, join_channel = "#test")
        
        nick1, client1 = clients[0]  
        
        irc_session.set_channel_mode(client1, nick1, "#test", "+m")
                
        for nick, client in clients:
            irc_session.verify_relayed_mode(client, from_nick=nick1, channel="#test", mode="+m")        
            

    def test_channel_mode18(self, irc_session):
        """
        Two clients connect to the server and join the same channel.
        
        The first one should be granted operator privileges, the second one
        shouldn't. The second tries to set the channel to be moderated (+m)
        and is denied because channel operator privileges are required to do so
        """
        
        clients = irc_session.connect_clients(2, join_channel = "#test")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1]  
        
        irc_session.set_channel_mode(client2, nick2, "#test", "+m", expect_ops_needed = True)


@pytest.mark.category("MODES")
class TestChannelMembershipMODE(object):

    def test_channel_membership_mode01(self, irc_session):
        """
        Two users connect to the server. The first one joins #test, the second
        one does not.
        
        The second user tries to set the first user's member status mode in #test 
        to +v. The second user does not have channel operator privileges in
        #test, and cannot do this (the user is also not in the channel,
        but the root cause of failure is the lack of privileges)
        """
         
        client1 = irc_session.connect_user("user1", "User One")

        client1.send_cmd("JOIN #test")
        irc_session.verify_join(client1, "user1", "#test")  

        client2 = irc_session.connect_user("user2", "User Two")
        
        irc_session.set_channel_mode(client2, "user2", "#test", "+v", "user1", expect_ops_needed = True)      

    def test_channel_membership_mode02(self, irc_session):
        """
        Two users connect to the server and they both join the #test channel.
        
        The second user tries to set the first user's member status mode in #test 
        to +v. The second user does not have channel operator privileges in
        #test, and cannot do this.
        """

        clients = irc_session.connect_clients(2, join_channel = "#test")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1]  
        
        irc_session.set_channel_mode(client2, nick2, "#test", "+v", "user1", expect_ops_needed = True)

    def test_channel_membership_mode03(self, irc_session):
        """
        Ten users connect to the server and they all join the #test channel.
        
        The first user to join the channel (the operator) gives voice privileges
        to user2 (+v)
        
        We check that everyone in the channel receives the relay of the MODE
        """  
        
        clients = irc_session.connect_clients(10, join_channel = "#test")
        
        nick1, client1 = clients[0]  
        
        irc_session.set_channel_mode(client1, nick1, "#test", "+v", "user2")
                
        for nick, client in clients:
            irc_session.verify_relayed_mode(client, from_nick=nick1, channel="#test", mode="+v", mode_nick="user2")


    def test_channel_membership_mode04(self, irc_session):
        """
        Ten users connect to the server and they all join the #test channel.
        
        The following happens:
        
        - user1 gives user2 operator privileges in the channel. We check
          that everyone receives the relay.
        - user2 gives voice privileges to user3. We check that everyone
          receives the relay.
        - user1 takes away the operator privileges from user2. We check
          that everyone receives the relay.
        - user2 (who is no longer an operator) tries to give voice
          privileges to user4 but is denied.
        """  
                
        clients = irc_session.connect_clients(5, join_channel = "#test")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1]  
        
        irc_session.set_channel_mode(client1, nick1, "#test", "+o", "user2")
        for nick, client in clients:
            irc_session.verify_relayed_mode(client, from_nick=nick1, channel="#test", mode="+o", mode_nick="user2")                                   

        irc_session.set_channel_mode(client2, nick2, "#test", "+v", "user3")
        for nick, client in clients:
            irc_session.verify_relayed_mode(client, from_nick=nick2, channel="#test", mode="+v", mode_nick="user3")                                   

        irc_session.set_channel_mode(client1, nick1, "#test", "-o", "user2")
        for nick, client in clients:
            irc_session.verify_relayed_mode(client, from_nick=nick1, channel="#test", mode="-o", mode_nick="user2")                                   

        irc_session.set_channel_mode(client2, nick2, "#test", "+v", "user4", expect_ops_needed=True)


    def test_channel_membership_mode05(self, irc_session):
        """
        Connects eleven users to the server, and has them join
        the following channels, and set the following privileges:
        (@ denotes channel operators, and + denotes a user with voice privileges):
        
        #test1: @user1, user2, user3
        #test2: @user2
        #test3: @user3, @user4, user5, user6
        #test4: @user7, +user8, +user9, user1, user2
        #test5: @user1, @user5 
        
        Not in a channel: user10, user11  
        """
        irc_session.connect_and_join_channels(channels3)


@pytest.mark.category("MODES")
class TestPermissionsPRIVMSG(BaseTestPermissions):

    def test_permissions_privmsg1(self, irc_session):
        """
        Test that, in a moderated channel, users without voice privileges
        cannot send messages to the channel.
        """
        
        clients = self._join_and_mode(irc_session, 3, "#test", "+m")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1]  
        
        client2.send_cmd("PRIVMSG #test :Hello from %s!" % nick2)
        
        irc_session.get_reply(client2, expect_code = replies.ERR_CANNOTSENDTOCHAN, expect_nick = nick2, 
                       expect_nparams = 2, expect_short_params = ["#test"],
                       long_param_re = "Cannot send to channel")           
        

    def test_permissions_privmsg2(self, irc_session):
        """
        Test that, in a moderated channel, the channel operator
        can send messages to the channel.
        """
        
        clients = self._join_and_mode(irc_session, 3, "#test", "+m")
        
        nick1, client1 = clients[0]  
        
        self._privmsg(irc_session, client1, nick1, "#test", clients)
        

    def test_permissions_privmsg3(self, irc_session):
        """
        Test that, in a moderated channel, a user with voice privileges
        can send messages to the channel.
        """

        clients = self._join_and_mode(irc_session, 3, "#test", "+m")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1] 
        
        irc_session.set_channel_mode(client1, nick1, "#test", "+v", nick2)     
        for nick, client in clients:
            irc_session.verify_relayed_mode(client, from_nick=nick1, channel="#test", mode="+v", mode_nick=nick2)                                   

        self._privmsg(irc_session, client2, nick2, "#test", clients)        
        

    def test_permissions_privmsg4(self, irc_session):
        """
        Test that, in a moderated channel, a user who has been granted channel operator
        privileges can send messages to the channel.
        """
                
        clients = self._join_and_mode(irc_session, 3, "#test", "+m")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1] 
        
        irc_session.set_channel_mode(client1, nick1, "#test", "+o", nick2)       
        for nick, client in clients:
            irc_session.verify_relayed_mode(client, from_nick=nick1, channel="#test", mode="+o", mode_nick=nick2)                                   
        
        self._privmsg(irc_session, client2, nick2, "#test", clients)   
        

    def test_permissions_privmsg5(self, irc_session):
        """
        Test that, in a moderated channel, a user who has been granted
        voice privileges and then has had them removed cannot send
        messages to the channel.
        """
        
        clients = self._join_and_mode(irc_session, 3, "#test", "+m")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1] 
        
        irc_session.set_channel_mode(client1, nick1, "#test", "+v", nick2)       
        for nick, client in clients:
            irc_session.verify_relayed_mode(client, from_nick=nick1, channel="#test", mode="+v", mode_nick=nick2)                                   
        
        irc_session.set_channel_mode(client1, nick1, "#test", "-v", nick2)       
        for nick, client in clients:
            irc_session.verify_relayed_mode(client, from_nick=nick1, channel="#test", mode="-v", mode_nick=nick2)                                   
        
        client2.send_cmd("PRIVMSG #test :Hello from %s!" % nick2)
        
        irc_session.get_reply(client2, expect_code = replies.ERR_CANNOTSENDTOCHAN, expect_nick = nick2, 
                       expect_nparams = 2, expect_short_params = ["#test"],
                       long_param_re = "Cannot send to channel")                
        
        

    def test_permissions_notice(self, irc_session):
        """
        Test that, in a moderated channel, a user who has does not
        have voice privileges will not receive an error if they send
        a NOTICE to the channel.
        """
                
        clients = self._join_and_mode(irc_session, 3, "#test", "+m")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1]  
        
        client2.send_cmd("NOTICE #test :Hello from %s!" % nick2)
        
        irc_session.get_reply(client2, expect_timeout = True)


@pytest.mark.category("MODES_TOPIC")
class TestPermissionsTOPIC(BaseTestPermissions):

    def test_permissions_topic1(self, irc_session):
        """
        Test that a user without channel operator privileges cannot
        set the topic in a channel with the +t mode
        """
        
        clients = self._join_and_mode(irc_session, 3, "#test", "+t")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1]  
        
        client2.send_cmd("TOPIC #test :Hello")
        
        irc_session.get_reply(client2, expect_code = replies.ERR_CHANOPRIVSNEEDED, expect_nick = nick2, 
                   expect_nparams = 2, expect_short_params = ["#test"],
                   long_param_re = "You're not channel operator")


    def test_permissions_topic2(self, irc_session):
        """
        Test that a user who has been granted channel operator privileges can
        set the topic in a channel with the +t mode
        """

        clients = self._join_and_mode(irc_session, 3, "#test", "+t")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1] 
        
        irc_session.set_channel_mode(client1, nick1, "#test", "+o", nick2)       
        for nick, client in clients:
            irc_session.verify_relayed_mode(client, from_nick=nick1, channel="#test", mode="+o", mode_nick=nick2)                                   
        
        client2.send_cmd("TOPIC #test :Hello")
        for nick, client in clients:
            irc_session.verify_relayed_topic(client, from_nick=nick2, channel="#test", topic="Hello")


class TestPermissionsOPER(BaseTestPermissions):

    @pytest.mark.category("OPER")
    def test_permissions_oper1(self, irc_session):
        """
        Check that an IRCop can set a channel to be moderated
        not being a channel operator.
        """
        
        clients = irc_session.connect_clients(3, join_channel = "#test")
        
        nick2, client2 = clients[1] 
        
        self._oper(irc_session, client2, nick2)
        
        irc_session.set_channel_mode(client2, nick2, "#test", "+m")
                
        for nick, client in clients:
            irc_session.verify_relayed_mode(client, from_nick=nick2, channel="#test", mode="+m")


    @pytest.mark.category("OPER")
    def test_permissions_oper2(self, irc_session):
        """
        Check that an IRCop can grant voice privileges to someone on a channel
        despite not being a channel operator.
        """
        
        clients = irc_session.connect_clients(3, join_channel = "#test")
        
        nick2, client2 = clients[1] 
        
        self._oper(irc_session, client2, nick2)
        
        irc_session.set_channel_mode(client2, nick2, "#test", "+v", "user3")
                
        for nick, client in clients:
            irc_session.verify_relayed_mode(client, from_nick=nick2, channel="#test", mode="+v", mode_nick="user3")

    @pytest.mark.category("OPER")
    def test_permissions_oper3(self, irc_session):
        """
        Check that an IRCop can send messages to a moderated channel despite
        not being a channel operator.
        """
        
        clients = self._join_and_mode(irc_session, 3, "#test", "+m")
        
        nick2, client2 = clients[1] 
        
        self._oper(irc_session, client2, nick2)

        self._privmsg(irc_session, client2, nick2, "#test", clients)

    @pytest.mark.category("OPER_TOPIC")
    def test_permissions_oper4(self, irc_session):
        """
        Check that an IRCop can change the topic in a channel with +t despite
        not being a channel operator.
        """
                
        clients = self._join_and_mode(irc_session, 3, "#test", "+t")
        
        nick2, client2 = clients[1] 
        
        self._oper(irc_session, client2, nick2)
                
        client2.send_cmd("TOPIC #test :Hello")
        for nick, client in clients:
            irc_session.verify_relayed_topic(client, from_nick=nick2, channel="#test", topic="Hello")




@pytest.mark.category("AWAY")
class TestAWAY(object):       
    
    def _away(self, irc_session, client, nick, msg):
        """
        Makes user `nick` go away with message `msg`
        """
        client.send_cmd("AWAY :%s" % msg)
        irc_session.get_reply(client, expect_code = replies.RPL_NOWAWAY, expect_nick = nick,
                       expect_nparams = 1, long_param_re = "You have been marked as being away")    


    def _unaway(self, irc_session, client, nick):
        """
        Makes user `nick` return from away
        """
        client.send_cmd("AWAY")
        irc_session.get_reply(client, expect_code = replies.RPL_UNAWAY, expect_nick = nick,
                       expect_nparams = 1, long_param_re = "You are no longer marked as being away")    
    
    
    def test_away1(self, irc_session):
        """
        Makes a user go away.
        """
        
        client1 = irc_session.connect_user("user1", "User One")
        
        self._away(irc_session, client1, "user1", "I'm not here")
        
        
    def test_away2(self, irc_session):
        """
        Makes a user go away and then return from away.
        """

        client1 = irc_session.connect_user("user1", "User One")
        
        self._away(irc_session, client1, "user1", "I'm not here")
        self._unaway(irc_session, client1, "user1")
        
        
    def test_away3(self, irc_session):
        """
        Makes a user return from away (not already being away)
        """
        
        client1 = irc_session.connect_user("user1", "User One")
        
        self._unaway(irc_session, client1, "user1")
        
        
    def test_away4(self, irc_session):
        """
        Check that if a user contacts another user who is away,
        they get the away message back.
        """
        
        clients = irc_session.connect_clients(2)
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1]          

        away_msg = "I'm not here"

        self._away(irc_session, client1, "user1", away_msg)
        
        client2.send_cmd("PRIVMSG user1 :Hello")
        
        irc_session.get_reply(client2, expect_code = replies.RPL_AWAY, expect_nick = nick2,
                       expect_nparams = 2, expect_short_params = ["user1"],
                       long_param_re = away_msg)           


    def test_away5(self, irc_session):
        """
        Check that if a user contacts another user who is away,
        and uses NOTICE, they get nothing back.
        """
                
        clients = irc_session.connect_clients(2)
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1]          

        away_msg = "I'm not here"

        self._away(irc_session, client1, "user1", away_msg)
        
        client2.send_cmd("NOTICE user1 :Hello")
        
        irc_session.get_reply(client2, expect_timeout = True)
        
                
    def test_away6(self, irc_session):
        """
        Check that RPL_AWAY replies are only sent in response to messages
        from users, not in response to messages sent to channels where
        that the user is in.
        """
        
        clients = irc_session.connect_clients(2, join_channel = "#test")
        
        nick1, client1 = clients[0]  
        nick2, client2 = clients[1]          

        away_msg = "I'm not here"

        self._away(irc_session, client1, "user1", away_msg)
        
        client2.send_cmd("PRIVMSG #test :Hello")
        irc_session.verify_relayed_privmsg(client1, from_nick=nick2, recip="#test", msg="Hello")
        irc_session.get_reply(client2, expect_timeout = True)        


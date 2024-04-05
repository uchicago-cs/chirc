import subprocess
import tempfile
import random
import os
import shutil
import re
import string

import chirc.replies as replies
from chirc.client import ChircClient
from chirc.types import ReplyTimeoutException
import pytest
import time



class SingleIRCSession:
    '''
    Class used to manage an IRC session involving a single server.
    At the start of the session, the server is started and we can connect
    to it with one or more clients (which are constructed through this class).
    The class also includes methods to perform common IRC actions (e.g.,
    sending a message from one user to another, joining a channel, etc.)
    and verifying that they were performed correctly.
    '''

    def __init__(self, chirc_exe = None, msg_timeout = 0.1,
                 chirc_port = None, loglevel = -1, debug = False,
                 irc_network = None, irc_network_server = None, external_chirc_port=None):
        if chirc_exe is None:
            self.chirc_exe = "../build/chirc"
        else:            
            self.chirc_exe = chirc_exe

        if not (os.path.exists(self.chirc_exe) and os.path.isfile(self.chirc_exe) and os.access(self.chirc_exe, os.X_OK)):
            raise RuntimeError("{} does not exist or it is not executable".format(self.chirc_exe))

        if irc_network is not None:
            assert irc_network_server in irc_network

            self.chirc_port = irc_network_server.port
            self.randomize_ports = False
            self.irc_network = irc_network
            self.irc_network_server = irc_network_server
        else:
            if chirc_port is None:
                self.chirc_port = 7776
                self.randomize_ports = False
            elif chirc_port == -1:
                self.chirc_port = None
                self.randomize_ports = True
            else:
                self.chirc_port = chirc_port
                self.randomize_ports = False
            self.irc_network = None
            self.irc_network_server = None

        self.msg_timeout = msg_timeout
        self.loglevel = loglevel
        self.debug = debug
        self.external_chirc_port = external_chirc_port

        random_str = "".join([random.choice(string.ascii_letters + string.digits) for _ in range(8)])
        self.oper_password = "oper-{}".format(random_str)
        self.started = False
        self.clients = []

    # Testing functions
    
    def _assert_equals(self, a, b, explanation, irc_msg = None):
        if irc_msg is not None:
            explanation = explanation + "\n\nMESSAGE: {}".format(irc_msg.raw(bookends=True))
        
        assert a == b, explanation

    def _assert_is_none(self, a, explanation, irc_msg = None):
        if irc_msg is not None:
            explanation = explanation + "\n\nMESSAGE: {}".format(irc_msg.raw(bookends=True))
        
        assert a is None, explanation

    def _assert_is_not_none(self, a, explanation, irc_msg = None):
        if irc_msg is not None:
            explanation = explanation + "\n\nMESSAGE: {}".format(irc_msg.raw(bookends=True))
        
        assert a is not None, explanation
        
    def _assert_in(self, x, l, explanation, irc_msg = None):
        if irc_msg is not None:
            explanation = explanation + "\n\nMESSAGE: {}".format(irc_msg.raw(bookends=True))
        
        assert x in l, explanation        
    

    # Start/end IRC session

    def start_session(self):
        if self.external_chirc_port is not None:
            self.started = True
            return

        self.tmpdir = tempfile.mkdtemp()
        
        if self.randomize_ports:
            self.port = random.randint(10000,60000)
        else:
            self.port = self.chirc_port
 
        if self.randomize_ports:
            tries = 10
        else:
            tries = 1


        while tries > 0:

            if self.irc_network is not None:
                network_file = self.tmpdir + "/network.txt"
                with open(network_file, "w") as f:
                    for server in self.irc_network:
                        line = "{},{},{},{}".format(server.servername,
                                                    server.hostname,
                                                    server.port,
                                                    server.passwd)
                        print(line, file=f)

                chirc_cmd = [os.path.abspath(self.chirc_exe), "-n", network_file,
                             "-s", self.irc_network_server.servername]
            else:
                chirc_cmd = [os.path.abspath(self.chirc_exe), "-p", str(self.port)]

            chirc_cmd += ["-o", self.oper_password]


            if self.loglevel == -1:
                chirc_cmd.append("-q")
            elif self.loglevel == 1:
                chirc_cmd.append("-v")
            elif self.loglevel == 2:
                chirc_cmd.append("-vv")

            self.chirc_proc = subprocess.Popen(chirc_cmd, cwd = self.tmpdir)
            time.sleep(0.01)
            rc = self.chirc_proc.poll()        
            if rc != None:
                tries -=1
                if tries == 0:
                    pytest.fail("chirc process failed to start. rc = %i" % rc)
                else:
                    if self.randomize_ports:
                        self.port = random.randint(10000,60000)
            else:
                break        

        self.started = True
        
    def end_session(self):
        if not self.started:
            return

        for c in self.clients:
            self.disconnect_client(c)

        if self.external_chirc_port is None:
            rc = self.chirc_proc.poll()
            if rc is not None:
                if rc != 0:
                    shutil.rmtree(self.tmpdir)
                    pytest.fail("chirc process failed during test. rc = %i" % rc)
            else:
                self.chirc_proc.kill()
            self.chirc_proc.wait()
            shutil.rmtree(self.tmpdir)

        self.started = False

    # Client connect/disconnect        
        
    def get_client(self, nodelay = False):
        if self.external_chirc_port is not None:
            port = self.external_chirc_port
        else:
            port = self.port
        c = ChircClient(msg_timeout = self.msg_timeout, port=port, nodelay = nodelay)
        self.clients.append(c)
        return c
        
    def disconnect_client(self, c):
        c.disconnect()
        self.clients.remove(c)
    
    def connect_user(self, nick, username):
        client = self.get_client()
        
        client.send_cmd("NICK %s" % nick)
        client.send_cmd("USER %s * * :%s" % (nick, username))
        
        self.verify_welcome_messages(client, nick)
        self.verify_lusers(client, nick)
        self.verify_motd(client, nick)
        
        return client    
    
    def connect_clients(self, numclients, join_channel = None):
        clients = []
        for i in range(numclients):
            nick = "user%i" % (i+1)
            username = "User %s" % nick
            client =  self.connect_user(nick, username)
            clients.append( (nick, client) )
        
        if join_channel != None:
            self.join_channel(clients, join_channel)

        return clients       
    
    def connect_and_join_channels(self, channels, aways = [], ircops = [], test_names = False):
        users = {}
        
        if None in channels:
            for user in channels[None]:
                if user not in users:
                    client = self.connect_user(user, user)
                    users[user] = client        
        
        channelsl = sorted([k for k in channels.keys() if k is not None])
        
        for channel in channelsl:
            channelusers = channels[channel]
            joined = []
            joinedp = []

            op = channelusers[0][1:]
            if op not in users:
                client = self.connect_user(op, op)
                users[op] = client
                
            if test_names:
                expect_names = [channelusers[0]]
            else:
                expect_names = None
                
            users[op].send_cmd("JOIN %s" % channel)
            self.verify_join(users[op], op, channel, expect_names = expect_names)  
            joined.append(op)
            joinedp.append(channelusers[0])
                
            for user in channelusers[1:]:
                if user[0] in ("@", "+"):
                    nick = user[1:]
                else:
                    nick = user
                    
                if nick not in users:
                    client = self.connect_user(nick, nick)
                    users[nick] = client
                    
                if test_names:
                    expect_names = joinedp + [nick]
                else:
                    expect_names = None                        
                    
                users[nick].send_cmd("JOIN %s" % channel)
                self.verify_join(users[nick], nick, channel, expect_names = expect_names)  
                
                for user2 in joined:
                    self.verify_relayed_join(users[user2], from_nick = None, channel=channel)                
                joined.append(nick)
                joinedp.append(user)
                
                if user[0] in ("@","+"):
                    if user[0] == "@":
                        mode = "+o"
                    elif user[0] == "+":
                        mode = "+v"

                    self.set_channel_mode(users[op], op, channel, mode, nick)
                    
                    for user2 in joined:
                        self.verify_relayed_mode(users[user2], from_nick=op, channel=channel, mode=mode, mode_nick=nick)
                            
        for user in aways:
            users[user].send_cmd("AWAY :I'm away")
            self.get_reply(users[user], expect_code = replies.RPL_NOWAWAY, expect_nick = user,
                           expect_nparams = 1, long_param_re = "You have been marked as being away")             

        for user in ircops:
            users[user].send_cmd("OPER %s %s" % (user, self.oper_password))
            self.get_reply(users[user], expect_code = replies.RPL_YOUREOPER, expect_nick = user, 
                           expect_nparams = 1, long_param_re = "You are now an IRC operator")  
                            
        return users
    
    
    # IRC actions   

    def join_channel(self, clients, channel):
        for (nick, client) in clients:
            client.send_cmd("JOIN %s" % channel)
            self.verify_join(client, nick, channel)  
            
        relayed = len(clients) - 1
        for (nick, client) in clients:
            for i in range(relayed):
                self.verify_relayed_join(client, from_nick = None, channel=channel)
            relayed -= 1            
            
    def part_channel(self, clients, channel):
        clients2 = clients[:]
        
        for (nick1, client1) in clients:
            client1.send_cmd("PART #test :%s is out of here!" % nick1)
            self.verify_relayed_part(client1, from_nick=nick1, channel=channel, msg="%s is out of here!" % nick1)  
            
            clients2.remove( (nick1, client1) )
            
            for (nick2, client2) in clients2:
                self.verify_relayed_part(client2, from_nick=nick1, channel=channel, msg="%s is out of here!" % nick1)  
        
      
    def set_user_mode(self, client, nick, nick_mode, mode, expect_wrong_mode=False, expect_relay=True):
        client.send_cmd("MODE %s %s" % (nick_mode, mode))
        
        if nick != nick_mode:
            self.get_reply(client, expect_code = replies.ERR_USERSDONTMATCH, expect_nick = nick, 
                           expect_nparams = 1,
                           long_param_re = "Cannot change mode for other users")
            return
        
        if expect_wrong_mode:
            self.get_reply(client, expect_code = replies.ERR_UMODEUNKNOWNFLAG, expect_nick = nick, 
                           expect_nparams = 1,
                           long_param_re = "Unknown MODE flag")            
        else:
            if expect_relay:
                reply = self.get_message(client, expect_prefix = True, expect_cmd = "MODE", 
                                         expect_nparams = 2, expect_short_params = [nick_mode],
                                         long_param_re = mode)
                self._assert_equals(reply.prefix.hostname, nick, 
                                    explanation = "Expected MODE's prefix to be nick '{}'".format(nick),
                                    irc_msg = reply)                
            else:
                self.get_reply(client, expect_timeout = True)            
        
    def set_channel_mode(self, client, nick, channel, mode = None, nick_mode = None, expect_mode = None, 
                      expect_wrong_channel=False, expect_wrong_mode = False, expect_ops_needed = False,
                      expect_not_on_channel=False):
        if mode is None and nick_mode is None:
            client.send_cmd("MODE %s" % channel)
        elif nick_mode is None:
            client.send_cmd("MODE %s %s" % (channel, mode))
        else:
            client.send_cmd("MODE %s %s %s" % (channel, mode, nick_mode))
            
        if expect_wrong_channel:
            self.get_reply(client, expect_code = replies.ERR_NOSUCHCHANNEL, expect_nick = nick, 
                       expect_nparams = 2, expect_short_params = [channel],
                       long_param_re = "No such channel")
            return

        if mode is None and nick_mode is None:
            reply = self.get_reply(client, expect_code = replies.RPL_CHANNELMODEIS, expect_nick = nick, 
                                   expect_nparams = 2, expect_short_params = [channel])
            mode_string = reply.params[-1]
            self._assert_equals(mode_string[0], "+", 
                                explanation = "Returned mode string does not start with '+'",
                                irc_msg = reply)            
            mode_string = mode_string[1:]
            if expect_mode is not None:
                self._assert_equals(len(mode_string), len(expect_mode), 
                                    explanation = "Expected mode string to have length {}".format(len(expect_mode)),
                                    irc_msg = reply)            
                
                for m in expect_mode:        
                    self._assert_in(m, mode_string, 
                                    explanation = "Expected mode string to have '{}', got this instead: {}".format(m, mode_string),
                                    irc_msg = reply)                                
        else:
            if expect_wrong_mode:
                self.get_reply(client, expect_code = replies.ERR_UNKNOWNMODE, expect_nick = nick, 
                           expect_nparams = 2, expect_short_params = [mode[1]],
                           long_param_re = "is unknown mode char to me for (?P<channel>.+)", 
                           long_param_values = {"channel":channel})
                
            if expect_ops_needed:
                self.get_reply(client, expect_code = replies.ERR_CHANOPRIVSNEEDED, expect_nick = nick, 
                           expect_nparams = 2, expect_short_params = [channel],
                           long_param_re = "You're not channel operator")  
                
            if nick_mode is not None and expect_not_on_channel:
                self.get_reply(client, expect_code = replies.ERR_USERNOTINCHANNEL, expect_nick = nick, 
                           expect_nparams = 3, expect_short_params = [nick_mode, channel],
                           long_param_re = "They aren't on that channel")
            
            
    # Message/reply getters

    def get_reply(self, client, expect_code = None, expect_nick = None, expect_nparams = None,
                  expect_short_params = None, long_param_re = None, long_param_values = None,
                  expect_timeout = False):
        try:
            msg = client.get_message()
            
            if expect_timeout:
                pytest.fail("Was not expecting a reply, but got one:\n" + msg.raw(bookends=True))                
        except EOFError:
            pytest.fail("Server closed connection unexpectedly. Possible segfault in server?")                
        except ReplyTimeoutException as rte:
            if expect_timeout:
                return None
            
            if len(rte.bytes_received) == 0:
                failmsg = "Expected a reply but got none (no bytes received)"
            else:
                failmsg = "Expected a reply but did not get valid reply terminated with \\r\\n. Bytes received:\n|||{}|||".format(rte.bytes_received)
            pytest.fail(failmsg)  
            
        self.verify_reply(msg, expect_code, expect_nick, expect_nparams, expect_short_params, long_param_re, long_param_values)
        
        return msg
    
    def get_ERR_NEEDMOREPARAMS_reply(self, client, expect_nick, expect_cmd):
        reply = self.get_reply(client, expect_code = replies.ERR_NEEDMOREPARAMS, 
                               expect_nick = expect_nick, expect_nparams = 2,
                               expect_short_params = [expect_cmd],
                               long_param_re = "Not enough parameters")
        return reply    
    
    def get_message(self, client, expect_prefix = None, expect_cmd = None, expect_nparams = None,
                  expect_short_params = None, long_param_re = None, long_param_values = None):
        try:
            msg = client.get_message()
        except EOFError:
            pytest.fail("Server closed connection unexpectedly. Possible segfault in server?")
            
        self.verify_message(msg, expect_prefix, expect_cmd, 
                           expect_nparams, expect_short_params, 
                           long_param_re, long_param_values)
        return msg    


    # Verifiers  
            
    def verify_message(self, msg, expect_prefix = None, expect_cmd = None,
                      expect_nparams = None, expect_short_params = None, 
                      long_param_re = None, long_param_values = None):
        
        if expect_prefix != None and expect_prefix:
            assert msg.prefix is not None, "Expected a prefix, but got none.\nMessage: {}".format(msg.raw(bookends=True))
            
        if expect_cmd != None:
            self._assert_equals(msg.cmd, expect_cmd, 
                                "Expected command {}, got {} instead".format(expect_cmd, msg.cmd),
                                irc_msg = msg)
            
        if expect_nparams != None:
            nparams = len(msg.params)
            self._assert_equals(nparams, expect_nparams, 
                                "Expected {} parameters, got {} instead".format(expect_nparams, nparams),
                                irc_msg = msg)
            
        if expect_short_params != None:
            for i, expect_p, p in zip (range(len(expect_short_params)), expect_short_params, msg.params):
                if expect_p is not None:
                    self._assert_equals(str(p), str(expect_p), 
                                "Expected parameter #{} to be {}, got {} instead".format(str(i+1), str(expect_p), str(p)),
                                irc_msg = msg)                    
                
        if long_param_re != None:
            lpre = "^:%s$" % long_param_re
            lp = msg.params[-1]
            match = re.match(lpre, lp)
            self._assert_is_not_none(match, "|||%s||| <-- Long parameter does not match regular expression: %s" % (lp, lpre), irc_msg = msg)
            if long_param_values != None:
                for k,v in long_param_values.items():
                    self._assert_equals(match.group(k), str(v), 
                                "Expected <{}> in long parameter to be {}, not {} (long parameter regex: {})".format(k, v, match.group(k), lpre),
                                irc_msg = msg)                            
            
    def verify_reply(self, msg, expect_code = None, expect_nick = None, expect_nparams = None,
                    expect_short_params = None, long_param_re = None, long_param_values = None):
        if expect_nparams is not None:
            nparams = expect_nparams + 1
        else:
            nparams = expect_nparams

        if expect_short_params is not None:
            if expect_nick is not None:
                short_params = [expect_nick] + expect_short_params
            else:
                short_params = [None] + expect_short_params
        else:
            if expect_nick is not None:
                short_params = [expect_nick]
            else:
                short_params = None

        self.verify_message(msg, expect_prefix = True, expect_cmd = expect_code, 
                            expect_nparams = nparams, expect_short_params = short_params, 
                            long_param_re = long_param_re, long_param_values = long_param_values)     
            
            
    def verify_welcome_messages(self, client, nick, user=None):
        r = []

        if user is None:
            user = nick

        reply = self.get_reply(client, expect_code = replies.RPL_WELCOME, expect_nick = nick, expect_nparams = 1,
                               long_param_re= "Welcome to the Internet Relay Network {}!{}.*".format(nick, user))
        r.append(reply)
        
        reply = self.get_reply(client, expect_code = replies.RPL_YOURHOST, expect_nick = nick, expect_nparams = 1)
        r.append(reply)
        
        reply = self.get_reply(client, expect_code = replies.RPL_CREATED, expect_nick = nick, expect_nparams = 1)
        r.append(reply)
        
        reply = self.get_reply(client, expect_code = replies.RPL_MYINFO, expect_nick = nick, expect_nparams = 4)
        r.append(reply)
        
        return r
    
    def verify_lusers(self, client, nick, expect_users = None, expect_servers=None,
                      expect_ops = None, expect_unknown = None, expect_channels = None,
                      expect_clients = None, expect_direct_servers=None):
        r = []
             
        reply = self.get_reply(client, expect_code = replies.RPL_LUSERCLIENT, expect_nick = nick, expect_nparams = 1)
        if expect_users is not None:
            self.verify_reply(reply,
                             long_param_re = r"There are (?P<users>\d+) users and 0 services on \d+ servers",
                             long_param_values = {"users":expect_users})
        if expect_servers is not None:
            self.verify_reply(reply,
                              long_param_re = r"There are \d+ users and 0 services on (?P<servers>\d+) servers",
                              long_param_values = {"servers":expect_servers})
        r.append(reply)
        
        reply = self.get_reply(client, expect_code = replies.RPL_LUSEROP, expect_nick = nick, 
                               expect_nparams = 2, long_param_re = r"operator\(s\) online")
        if expect_ops is not None:
            self.verify_reply(reply, expect_short_params = [expect_ops])
        r.append(reply)

        reply = self.get_reply(client, expect_code = replies.RPL_LUSERUNKNOWN, expect_nick = nick, 
                               expect_nparams = 2, long_param_re = r"unknown connection\(s\)")
        if expect_unknown is not None:
            self.verify_reply(reply, expect_short_params = [expect_unknown])
        r.append(reply)

        reply = self.get_reply(client, expect_code = replies.RPL_LUSERCHANNELS, expect_nick = nick, 
                               expect_nparams = 2, long_param_re = "channels formed")
        if expect_channels is not None:
            self.verify_reply(reply, expect_short_params = [expect_channels])
        r.append(reply)

        reply = self.get_reply(client, expect_code = replies.RPL_LUSERME, expect_nick = nick, expect_nparams = 1)
        if expect_clients is not None:
            self.verify_reply(reply,
                             long_param_re = r"I have (?P<clients>\d+) clients and \d+ servers",
                             long_param_values = {"clients":expect_clients})
        if expect_direct_servers is not None:
            self.verify_reply(reply,
                              long_param_re = r"I have \d+ clients and (?P<servers>\d+) servers",
                              long_param_values = {"servers":expect_direct_servers})
        r.append(reply)
        
        return r
    
    def verify_motd(self, client, nick, expect_motd = None):
        r = []
             
        if expect_motd is None:
            reply = self.get_reply(client, expect_code = replies.ERR_NOMOTD, expect_nick = nick, 
                                   expect_nparams = 1, long_param_re = "MOTD File is missing")
            r.append(reply)
        else:
            reply = self.get_reply(client, expect_code = replies.RPL_MOTDSTART, expect_nick = nick, 
                                   expect_nparams = 1, long_param_re = "- .* Message of the day - ")
            r.append(reply)
            
            motd_lines = expect_motd.strip().split("\n")

            for l in motd_lines:
                reply = self.get_reply(client, expect_code = replies.RPL_MOTD, expect_nick = nick, 
                                       expect_nparams = 1, long_param_re = "- " + l)                    
                r.append(reply)

            reply = self.get_reply(client, expect_code = replies.RPL_ENDOFMOTD, expect_nick = nick, 
                                   expect_nparams = 1, long_param_re = "End of MOTD command")     
            r.append(reply)

        return r
    
    def verify_disconnect(self, client):
        try:
            client.get_message()
        except EOFError:
            return
        except ReplyTimeoutException:
            pytest.fail("Server did not close connection after QUIT")
        else:
            pytest.fail("Server did not close connection after QUIT")                
    
    def verify_join(self, client, nick, channel, expect_topic = None, expect_names = None):
        self.verify_relayed_join(client, nick, channel)
        
        if expect_topic != None:
            self.get_reply(client, expect_code = replies.RPL_TOPIC, expect_nick = nick,
                           expect_nparams = 2, expect_short_params = [channel], long_param_re=expect_topic)
        
        self.verify_names(client, nick, expect_names = expect_names)
        
    def verify_relayed_join(self, client, from_nick, channel):
        reply = self.get_message(client, expect_prefix = True, expect_cmd = "JOIN", 
                                 expect_nparams = 1, expect_short_params = [channel])
        if from_nick != None:
            self._assert_equals(reply.prefix.nick, from_nick, 
                                explanation = "Expected JOIN's prefix to have nick '{}'".format(from_nick), 
                                irc_msg = reply)

    def verify_relayed_part(self, client, from_nick, channel, msg):
        if msg != None:
            expect_nparams = 2
        else:
            expect_nparams = 1
        
        reply = self.get_message(client, expect_prefix = True, expect_cmd = "PART", 
                                 expect_nparams = expect_nparams, expect_short_params = [channel],
                                 long_param_re = msg)
        self._assert_equals(reply.prefix.nick, from_nick, 
                            explanation = "Expected PART's prefix to have nick '{}'".format(from_nick), 
                            irc_msg = reply)
        

    def verify_relayed_quit(self, client, from_nick, msg):
        reply = self.get_message(client, expect_prefix = True, expect_cmd = "QUIT", 
                                 expect_nparams = 1, long_param_re = msg)
        self._assert_equals(reply.prefix.nick, from_nick, 
                            explanation = "Expected QUIT's prefix to have nick '{}'".format(from_nick), 
                            irc_msg = reply)

    def verify_relayed_nick(self, client, from_nick, newnick):
        reply = self.get_message(client, expect_prefix = True, expect_cmd = "NICK", 
                                 expect_nparams = 1, long_param_re = newnick)
        self._assert_equals(reply.prefix.nick, from_nick, 
                            explanation = "Expected NICK's prefix to have nick '{}'".format(from_nick), 
                            irc_msg = reply)
        
    def verify_relayed_privmsg(self, client, from_nick, recip, msg):
        reply = self.get_message(client, expect_prefix = True, expect_cmd = "PRIVMSG", 
                                 expect_nparams = 2, expect_short_params = [recip],
                                 long_param_re = msg)
        self._assert_equals(reply.prefix.nick, from_nick, 
                            explanation = "Expected PRIVMSG's prefix to have nick '{}'".format(from_nick), 
                            irc_msg = reply)

    def verify_relayed_topic(self, client, from_nick, channel, topic):
        reply = self.get_message(client, expect_prefix = True, expect_cmd = "TOPIC", 
                                 expect_nparams = 2, expect_short_params = [channel],
                                 long_param_re = topic)
        self._assert_equals(reply.prefix.nick, from_nick, 
                            explanation = "Expected TOPIC's prefix to have nick '{}'".format(from_nick), 
                            irc_msg = reply)

    def verify_relayed_mode(self, client, from_nick, channel, mode, mode_nick = None):
        if mode_nick is not None:
            expect_nparams = 3
            expect_short_params = [channel, mode, mode_nick]
        else:
            expect_nparams = 2
            expect_short_params = [channel, mode]
        reply = self.get_message(client, expect_prefix = True, expect_cmd = "MODE", 
                                 expect_nparams = expect_nparams, expect_short_params = expect_short_params)
        self._assert_equals(reply.prefix.nick, from_nick, 
                            explanation = "Expected MODE's prefix to have nick '{}'".format(from_nick), 
                            irc_msg = reply)
        
    def verify_relayed_notice(self, client, from_nick, recip, msg):
        reply = self.get_message(client, expect_prefix = True, expect_cmd = "NOTICE", 
                                 expect_nparams = 2, expect_short_params = [recip],
                                 long_param_re = msg)
        self._assert_equals(reply.prefix.nick, from_nick, 
                            explanation = "Expected NOTICE's prefix to have nick '{}'".format(from_nick), 
                            irc_msg = reply)
        
    def verify_names_single(self, reply, nick, expect_channel = None, expect_names = None):        
        if expect_channel is not None:
            if expect_channel == "*":
                self._assert_equals(reply.params[1], "*", 
                                    explanation = "Expected first parameter to be '*'", 
                                    irc_msg = reply)
                self._assert_equals(reply.params[2], "*", 
                                    explanation = "Expected second parameter to be '*'", 
                                    irc_msg = reply)
            else:
                self._assert_equals(reply.params[1], "=", 
                                    explanation = "Expected first parameter to be '='", 
                                    irc_msg = reply)
                self._assert_equals(reply.params[2], expect_channel, 
                                    explanation = "Expected channel in NAMES to be {}".format(expect_channel), 
                                    irc_msg = reply)

        if expect_names is not None:
            names = reply.params[3][1:].split(" ")
            self._assert_equals(len(names), len(expect_names), 
                                explanation = "Expected list of names to have {} entries" .format(len(expect_names)), 
                                irc_msg = reply)
            for name in expect_names:
                self._assert_in(name, names, 
                                explanation = "Expected {} in NAMES".format(name), 
                                irc_msg = reply)
        
    def verify_names(self, client, nick, expect_channel = None, expect_names = None):
        reply = self.get_reply(client, expect_code = replies.RPL_NAMREPLY, expect_nick = nick,
                               expect_nparams = 3)        
        self.verify_names_single(reply, nick, expect_channel, expect_names)
            
        if expect_channel is not None:
            expect_short_params = [expect_channel]
        else:
            expect_short_params = None
            
        self.get_reply(client, expect_code = replies.RPL_ENDOFNAMES, expect_nick = nick,
                       expect_short_params = expect_short_params, expect_nparams = 2)

    def verify_list(self, channels, client, nick, expect_topics = None):
        """
        User `nick` sends a LIST command and we verify the replies.
        `channels` is a dictionary mapping channel names to users in each channel.
        `expect_topics` is a dictionary mapping channel names to their topics
        """

        client.send_cmd("LIST")

        channelsl = set([k for k in channels.keys() if k is not None])
        numchannels = len(channelsl)

        for i in range(numchannels):
            reply = self.get_reply(client, expect_code = replies.RPL_LIST, expect_nick = nick,
                                          expect_nparams = 3)

            channel = reply.params[1]
            self._assert_in(channel, channelsl,
                                   explanation = "Received unexpected RPL_LIST for {}".format(channel),
                                   irc_msg = reply)

            numusers = int(reply.params[2])
            expect_numusers = len(channels[channel])
            self._assert_equals(numusers, expect_numusers,
                                       explanation = "Expected {} users in {}, got {}".format(expect_numusers, channel, numusers),
                                       irc_msg = reply)

            if expect_topics is not None:
                expect_topic = expect_topics[channel]
                topic = reply.params[3][1:]
                self._assert_equals(topic, expect_topic,
                                           explanation = "Expected topic for {} to be '{}', got '{}' instead".format(channel, expect_topic, topic),
                                           irc_msg = reply)

            channelsl.remove(channel)

        assert len(channelsl) == 0, "Did not receive RPL_LIST for these channels: {}".format(", ".join(channelsl))

        self.get_reply(client, expect_code = replies.RPL_LISTEND, expect_nick = nick,
                               expect_nparams = 1, long_param_re = "End of LIST")

    def verify_server_registration(self, client, passive_server, active_server):
        expect_short_params = [active_server.passwd, "0210"]
        reply = self.get_message(client, expect_prefix = True, expect_cmd = "PASS",
                                 expect_short_params = expect_short_params, expect_nparams = 3)

        self._assert_equals(reply.prefix.hostname, passive_server.servername,
                            explanation = "Expected prefix to be '{}'".format(passive_server.servername),
                            irc_msg = reply)

        expect_short_params = [passive_server.servername]
        reply = self.get_message(client, expect_prefix = True, expect_cmd = "SERVER",
                                 expect_short_params = expect_short_params, expect_nparams = 4)

        self._assert_equals(reply.prefix.hostname, passive_server.servername,
                            explanation = "Expected prefix to be '{}'".format(passive_server.servername),
                            irc_msg = reply)

    def verify_relayed_network_nick(self, client, from_server, expect_nick, expect_hopcount, expect_username,
                                    expect_servertoken, expect_mode, expect_fullname):
        expect_short_params = [expect_nick, expect_hopcount, expect_username]
        reply = self.get_message(client, expect_prefix = True, expect_cmd = "NICK",
                                 expect_short_params=expect_short_params, expect_nparams = 7)
        self._assert_equals(reply.prefix.hostname, from_server.servername,
                            explanation = "Expected NICK's prefix to be servername '{}'".format(from_server.servername),
                            irc_msg = reply)

class IRCNetworkServer:

    def __init__(self, servername, hostname, port, passwd):
        self.servername = servername
        self.hostname = hostname
        self.port = port
        self.passwd = passwd
        self.irc_session = None



class IRCNetworkSession:
    '''
    This class is used to manage multiple IRC sessions at the same time.
    It creates one SingleIRCSession object per server.
    '''

    def __init__(self, chirc_exe=None, msg_timeout = 0.1,
                 default_start_port=7776, loglevel=-1, debug=False):

        # We skip validating many of the parameters, because this will be done in
        # the SingleIRCSession constructor

        self.chirc_exe = chirc_exe
        self.msg_timeout = msg_timeout
        self.default_start_port = default_start_port
        self.loglevel = loglevel
        self.debug = debug
        self.servers = []

    def set_servers(self, num_servers):

        if self.default_start_port == -1:
            port = random.randint(10000,60000)
        else:
            port = self.default_start_port

        for i in range(num_servers):
            n = i+1
            servername = "irc-{}.example.net".format(n)
            hostname = "127.0.0.1"
            port = port + i
            passwd = "passwd{}".format(n)

            server = IRCNetworkServer(servername, hostname, port, passwd)
            self.servers.append(server)

        for server in self.servers:
            session =  SingleIRCSession(chirc_exe=self.chirc_exe,
                                        loglevel=self.loglevel,
                                        debug=self.debug,
                                        irc_network=self.servers,
                                        irc_network_server=server)
            server.irc_session = session

    def start_session(self, server_idx):
        self.servers[server_idx].irc_session.start_session()

    def end_sessions(self):
        for server in self.servers:
            server.irc_session.end_session()


import subprocess
import telnetlib
import random
import unittest
import time
import replies
import sys
import re
import tempfile
import shutil
import os

import tests

TESTING_PORT = "7776"
OPER_PASSWD = "foobar"

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

class CouldNotStartChircException(Exception):
    pass

class CouldNotConnectException(Exception):
    pass

class ServerDisconnectedException(Exception):
    pass

class ReplyTimeoutException(Exception):
    pass

class MessageNotWellFormedException(Exception):
    pass

class PrefixNotWellFormedException(Exception):
    pass

class IRCPrefix(object):
    def __init__(self, s):
        self._s = s
        
        self.nick = self.username = self.hostname = None
        
        if not "@" in s and not "!" in s:
            self.hostname = s[1:]
        elif "@" in s and "!" in s:
            match = re.match("^:(?P<nick>[^!@]+)!(?P<username>[^!@]+)@(?P<hostname>[^!@]+)$", s)
            if match == None:
                raise PrefixNotWellFormedException()
            else:
                # TODO: This could be validated further
                self.nick = match.group("nick")
                self.username = match.group("username")
                self.hostname = match.group("hostname")                
        else:
            raise PrefixNotWellFormedException()

class IRCMessage(object):
    def __init__(self, s):
        if s[-2:] != "\r\n":
            raise MessageNotWellFormedException()
        
        self._s = s[:-2]
        
        fields = self._s.split(" ")
        
        if len(fields) < 2:
            raise MessageNotWellFormedException()
        
        if fields[0][0] == ":":
            if len(fields) == 2: raise MessageNotWellFormedException()
            self.prefix = IRCPrefix(fields[0])
            self.cmd = fields[1]
            p = 2
        else:
            self.prefix = None
            self.cmd = fields[0]
            p = 1
            
        self.params = []
        
        while p < len(fields):
            if fields[p][0] == ":":
                self.params.append(" ".join(fields[p:]))
                break
            else:
                self.params.append(fields[p])
                p += 1
            
class ChircClient(object):
    
    def __init__(self, host = "localhost", port = TESTING_PORT, msg_timeout = 1.0):
        self.host = host
        self.port = port
        self.msg_timeout = msg_timeout
        
        tries = 3

        while tries > 0:
            try:
                self.client = telnetlib.Telnet("localhost", `self.port`, 1)
                break
            except Exception, e:
                tries -= 1
                time.sleep(0.1)

        if tries == 0:
            raise CouldNotConnectException()
    
    def disconnect(self):
        self.client.close()
        
    def get_message(self):
        msg = self.client.read_until("\r\n", timeout=self.msg_timeout)
        if msg[-2:] != "\r\n":
            raise ReplyTimeoutException()
        msg = IRCMessage(msg)
        return msg

    def send_cmd(self, cmd):
        self.client.write("%s\r\n" % cmd)
        
    def send_raw(self, raw):
        self.client.write(raw)

class ChircTestCase(unittest.TestCase):
    
    CHIRC_EXE = "./chirc"
    MESSAGE_TIMEOUT = 1.0
    INTERTEST_PAUSE = 0.0
    RANDOMIZE_PORTS = False
    DEFAULT_PORT = 7776

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        
        if self.RANDOMIZE_PORTS:
            self.port = random.randint(10000,60000)
        else:
            self.port = self.DEFAULT_PORT

        if tests.DEBUG:
            stdout = stderr = None
        else:
            stdout = open('/dev/null', 'w')
            stderr = subprocess.STDOUT
 
        tries = 3

        while tries > 0:
            self.chirc_proc = subprocess.Popen([os.path.abspath(ChircTestCase.CHIRC_EXE), "-p", `self.port`, "-o", OPER_PASSWD], stdout=stdout, stderr=stderr, cwd = self.tmpdir)
            rc = self.chirc_proc.poll()        
            if rc != None:
                self.fail("chirc process failed to start. rc = %i" % rc)
                tries -=1
                if self.RANDOMIZE_PORTS:
                    self.port = random.randint(10000,60000)
            else:
                break        
            
        self.clients = []
        
    def tearDown(self):
        for c in self.clients:
            self.disconnect_client(c)
        rc = self.chirc_proc.poll()
        if rc != None:
            self.fail("chirc process failed during test. rc = %i" % rc)
            shutil.rmtree(self.tmpdir)
        else:
            self.chirc_proc.kill()
        self.chirc_proc.wait()
        shutil.rmtree(self.tmpdir)
        time.sleep(self.INTERTEST_PAUSE)
        
    def get_client(self):
        c = ChircClient(msg_timeout = self.MESSAGE_TIMEOUT, port=self.port)
        self.clients.append(c)
        return c
        
    def disconnect_client(self, c):
        c.disconnect()
        self.clients.remove(c)
        
    def _msgAssertEqual(self, reply, value, expected, msg):
        assert_msg = "|||%s||| <-- %s" % (reply._s, msg)
        self.assertEqual(value, expected, assert_msg % (expected, value))
    
    def _test_message(self, msg, expect_prefix = None, expect_cmd = None,
                      expect_nparams = None, expect_short_params = None, 
                      long_param_re = None, long_param_values = None):
        
        if expect_prefix != None and expect_prefix:
            self.assertIsNotNone(msg.prefix, "Expected a prefix, but got none.")
            
        if expect_cmd != None:
            self._msgAssertEqual(msg, msg.cmd, expect_cmd, "Expected command %s, got %s instead")
            
        if expect_nparams != None:
            nparams = len(msg.params)
            self._msgAssertEqual(msg, nparams, expect_nparams, "Expected %i parameters, got %i instead")
            
        if expect_short_params != None:
            for i, expect_p, p in zip (range(len(expect_short_params)), expect_short_params, msg.params):
                if expect_p is not None:
                    self._msgAssertEqual(msg, str(p), str(expect_p), "Expected parameter #" + str(i+1) +" to be %s, got %s instead")
                
        if long_param_re != None:
            lpre = "^:%s$" % long_param_re
            lp = msg.params[-1]
            match = re.match(lpre, lp)
            self.assertIsNotNone(match, "|||%s||| <-- Long parameter does not match regular expression: %s" % (lp, lpre))
            if long_param_values != None:
                for k,v in long_param_values.items():
                    self.assertEqual(match.group(k), str(v), "Expected <%s> in long parameter to be %s, not %s (long parameter regex: %s)" % (k, v, match.group(k), lpre))
                    
    def _clients_connect(self, numclients, join_channel = None):
        clients = []
        for i in range(numclients):
            nick = "user%i" % (i+1)
            username = "User %s" % nick
            client =  self._connect_user(nick, username)
            clients.append( (nick, client) )
        
        if join_channel != None:
            self._clients_join(clients, join_channel)

        return clients       
    
    def _channels_connect(self, channels, aways = [], ircops = [], test_names = False):
        users = {}
        channelsl = channels.keys()
        channelsl.sort()
        for channel in channelsl:
            channelusers = channels[channel]
            joined = []
            joinedp = []
            if channel is None:
                for user in channelusers:
                    if not users.has_key(user):
                        client = self._connect_user(user, user)
                        users[user] = client
            else: 
                op = channelusers[0][1:]
                if not users.has_key(op):
                    client = self._connect_user(op, op)
                    users[op] = client
                    
                if test_names:
                    expect_names = [channelusers[0]]
                else:
                    expect_names = None
                    
                users[op].send_cmd("JOIN %s" % channel)
                self._test_join(users[op], op, channel, expect_names = expect_names)  
                joined.append(op)
                joinedp.append(channelusers[0])
                    
                for user in channelusers[1:]:
                    if user[0] in ("@", "+"):
                        nick = user[1:]
                    else:
                        nick = user
                        
                    if not users.has_key(nick):
                        client = self._connect_user(nick, nick)
                        users[nick] = client
                        
                    if test_names:
                        expect_names = joinedp + [nick]
                    else:
                        expect_names = None                        
                        
                    users[nick].send_cmd("JOIN %s" % channel)
                    self._test_join(users[nick], nick, channel, expect_names = expect_names)  
                    
                    for user2 in joined:
                        self._test_relayed_join(users[user2], from_nick = None, channel=channel)                
                    joined.append(nick)
                    joinedp.append(user)
                    
                    if user[0] in ("@","+"):
                        if user[0] == "@":
                            mode = "+o"
                        elif user[0] == "+":
                            mode = "+v"

                        self._channel_mode(users[op], op, channel, mode, nick)
                        
                        for user2 in joined:
                            self._test_relayed_mode(users[user2], from_nick=op, channel=channel, mode=mode, mode_nick=nick)
                            
        for user in aways:
            users[user].send_cmd("AWAY :I'm away")
            self.get_reply(users[user], expect_code = replies.RPL_NOWAWAY, expect_nick = user,
                           expect_nparams = 1, long_param_re = "You have been marked as being away")             

        for user in ircops:
            users[user].send_cmd("OPER %s %s" % (user, OPER_PASSWD))
            self.get_reply(users[user], expect_code = replies.RPL_YOUREOPER, expect_nick = user, 
                           expect_nparams = 1, long_param_re = "You are now an IRC operator")  
                            
        return users
                        
                    

    def _clients_join(self, clients, channel):
        for (nick, client) in clients:
            client.send_cmd("JOIN %s" % channel)
            self._test_join(client, nick, channel)  
            
        relayed = len(clients) - 1
        for (nick, client) in clients:
            for i in range(relayed):
                self._test_relayed_join(client, from_nick = None, channel=channel)
            relayed -= 1            
            
    def _clients_part(self, clients, channel):
        clients2 = clients[:]
        
        for (nick1, client1) in clients:
            client1.send_cmd("PART #test :%s is out of here!" % nick1)
            self._test_relayed_part(client1, from_nick=nick1, channel=channel, msg="%s is out of here!" % nick1)  
            
            clients2.remove( (nick1, client1) )
            
            for (nick2, client2) in clients2:
                self._test_relayed_part(client2, from_nick=nick1, channel=channel, msg="%s is out of here!" % nick1)  
        
      
    def _user_mode(self, client, nick, nick_mode, mode, expect_wrong_mode=False, expect_relay=True):
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
                self.assertEqual(reply.prefix.hostname, nick, "Expected MODE's prefix to be nick '%s': %s" % (nick, reply._s))
            else:
                self.assertRaises(ReplyTimeoutException, self.get_reply, client)    
            
        
    def _channel_mode(self, client, nick, channel, mode = None, nick_mode = None, expect_mode = None, 
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
            self.assertEqual(mode_string[0], "+", "Returned mode string does not start with '+': %s" % reply._s)
            mode_string = mode_string[1:]
            if expect_mode is not None:
                self.assertEqual(len(mode_string), len(expect_mode), "Expected mode string to have length %i, got this instead: %s" % (len(expect_mode), mode_string))
                
                for m in expect_mode:        
                    self.assertIn(m, mode_string, "Expected mode string to have '%s', got this instead: %s" % (m,mode_string))        
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
            
            
            
    def _test_reply(self, msg, expect_code = None, expect_nick = None, expect_nparams = None,
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
            short_params = None
        
        self._test_message(msg, expect_prefix = True, expect_cmd = expect_code, 
                           expect_nparams = nparams, expect_short_params = short_params, 
                           long_param_re = long_param_re, long_param_values = long_param_values)     
            
    def get_reply(self, client, expect_code = None, expect_nick = None, expect_nparams = None,
                  expect_short_params = None, long_param_re = None, long_param_values = None):
        msg = client.get_message()
        self._test_reply(msg, expect_code, expect_nick, expect_nparams, expect_short_params, long_param_re, long_param_values)
        return msg
    
    def get_message(self, client, expect_prefix = None, expect_cmd = None, expect_nparams = None,
                  expect_short_params = None, long_param_re = None, long_param_values = None):
        msg = client.get_message()
        self._test_message(msg, expect_prefix, expect_cmd, 
                           expect_nparams, expect_short_params, 
                           long_param_re, long_param_values)
        return msg    
            
    def _test_welcome_messages(self, client, nick):
        r = []

        reply = self.get_reply(client, expect_code = replies.RPL_WELCOME, expect_nick = nick, expect_nparams = 1)
        r.append(reply)
        
        reply = self.get_reply(client, expect_code = replies.RPL_YOURHOST, expect_nick = nick, expect_nparams = 1)
        r.append(reply)
        
        reply = self.get_reply(client, expect_code = replies.RPL_CREATED, expect_nick = nick, expect_nparams = 1)
        r.append(reply)
        
        reply = self.get_reply(client, expect_code = replies.RPL_MYINFO, expect_nick = nick, expect_nparams = 4)
        r.append(reply)
        
        return r
    
    def _test_lusers(self, client, nick, expect_users = None, expect_ops = None, expect_unknown = None, expect_channels = None, expect_clients = None):
        r = []
             
        reply = self.get_reply(client, expect_code = replies.RPL_LUSERCLIENT, expect_nick = nick, expect_nparams = 1)
        if expect_users is not None:
            self._test_reply(reply,
                             long_param_re = "There are (?P<users>\d+) users and 0 services on 1 servers", 
                             long_param_values = {"users":expect_users})
        r.append(reply)
        
        reply = self.get_reply(client, expect_code = replies.RPL_LUSEROP, expect_nick = nick, 
                               expect_nparams = 2, long_param_re = "operator\(s\) online")
        if expect_ops is not None:
            self._test_reply(reply, expect_short_params = [expect_ops])
        r.append(reply)

        reply = self.get_reply(client, expect_code = replies.RPL_LUSERUNKNOWN, expect_nick = nick, 
                               expect_nparams = 2, long_param_re = "unknown connection\(s\)")
        if expect_unknown is not None:
            self._test_reply(reply, expect_short_params = [expect_unknown])
        r.append(reply)

        reply = self.get_reply(client, expect_code = replies.RPL_LUSERCHANNELS, expect_nick = nick, 
                               expect_nparams = 2, long_param_re = "channels formed")
        if expect_channels is not None:
            self._test_reply(reply, expect_short_params = [expect_channels])
        r.append(reply)

        reply = self.get_reply(client, expect_code = replies.RPL_LUSERME, expect_nick = nick, expect_nparams = 1)
        if expect_clients is not None:
            self._test_reply(reply,
                             long_param_re = "I have (?P<clients>\d+) clients and (?P<servers>\d+) servers", 
                             long_param_values = {"clients":expect_clients})            
        r.append(reply)
        
        return r
    
    def _test_motd(self, client, nick, expect_motd = None):
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
                                   expect_nparams = 1, long_param_re = "- End of MOTD command")     
            r.append(reply)

        return r
    
    def _test_join(self, client, nick, channel, expect_topic = None, expect_names = None):
        self._test_relayed_join(client, nick, channel)
        
        if expect_topic != None:
            self.get_reply(client, expect_code = replies.RPL_TOPIC, expect_nick = nick,
                           expect_nparams = 2, expect_short_params = [channel], long_param_re=expect_topic)
        
        self._test_names(client, nick, expect_names = expect_names)
        
    def _test_relayed_join(self, client, from_nick, channel):
        reply = self.get_message(client, expect_prefix = True, expect_cmd = "JOIN", 
                                 expect_nparams = 1, expect_short_params = [channel])
        if from_nick != None:
            self.assertEqual(reply.prefix.nick, from_nick, "Expected JOIN's prefix to have nick '%s': %s" % (from_nick, reply._s))

    def _test_relayed_part(self, client, from_nick, channel, msg):
        if msg != None:
            expect_nparams = 2
        else:
            expect_nparams = 1
        
        reply = self.get_message(client, expect_prefix = True, expect_cmd = "PART", 
                                 expect_nparams = expect_nparams, expect_short_params = [channel],
                                 long_param_re = msg)
        self.assertEqual(reply.prefix.nick, from_nick, "Expected PART's prefix to have nick '%s': %s" % (from_nick, reply._s))

    def _test_relayed_quit(self, client, from_nick, msg):
        reply = self.get_message(client, expect_prefix = True, expect_cmd = "QUIT", 
                                 expect_nparams = 1, long_param_re = msg)
        self.assertEqual(reply.prefix.nick, from_nick, "Expected QUIT's prefix to have nick '%s': %s" % (from_nick, reply._s))

    def _test_relayed_nick(self, client, from_nick, newnick):
        reply = self.get_message(client, expect_prefix = True, expect_cmd = "NICK", 
                                 expect_nparams = 1, long_param_re = newnick)
        self.assertEqual(reply.prefix.nick, from_nick, "Expected NICK's prefix to have nick '%s': %s" % (from_nick, reply._s))
        
    def _test_relayed_privmsg(self, client, from_nick, recip, msg):
        reply = self.get_message(client, expect_prefix = True, expect_cmd = "PRIVMSG", 
                                 expect_nparams = 2, expect_short_params = [recip],
                                 long_param_re = msg)
        self.assertEqual(reply.prefix.nick, from_nick, "Expected PRIVMSG's prefix to have nick '%s': %s" % (from_nick, reply._s))

    def _test_relayed_topic(self, client, from_nick, channel, topic):
        reply = self.get_message(client, expect_prefix = True, expect_cmd = "TOPIC", 
                                 expect_nparams = 2, expect_short_params = [channel],
                                 long_param_re = topic)
        self.assertEqual(reply.prefix.nick, from_nick, "Expected TOPIC's prefix to have nick '%s': %s" % (from_nick, reply._s))

    def _test_relayed_mode(self, client, from_nick, channel, mode, mode_nick = None):
        if mode_nick is not None:
            expect_nparams = 3
            expect_short_params = [channel, mode, mode_nick]
        else:
            expect_nparams = 2
            expect_short_params = [channel, mode]
        reply = self.get_message(client, expect_prefix = True, expect_cmd = "MODE", 
                                 expect_nparams = expect_nparams, expect_short_params = expect_short_params)
        self.assertEqual(reply.prefix.nick, from_nick, "Expected MODE's prefix to have nick '%s': %s" % (from_nick, reply._s))
        
    def _test_relayed_notice(self, client, from_nick, recip, msg):
        reply = self.get_message(client, expect_prefix = True, expect_cmd = "NOTICE", 
                                 expect_nparams = 2, expect_short_params = [recip],
                                 long_param_re = msg)
        self.assertEqual(reply.prefix.nick, from_nick, "Expected NOTICE's prefix to have nick '%s': %s" % (from_nick, reply._s))
        
    def _test_names_single(self, reply, nick, expect_channel = None, expect_names = None):        
        if expect_channel is not None:
            if expect_channel == "*":
                self.assertEqual(reply.params[1], "*", "Expected first parameter to be '=': %s" % reply._s)
                self.assertEqual(reply.params[2], "*", "Expected second parameter to be '*': %s" % reply._s)
            else:
                self.assertEqual(reply.params[1], "=", "Expected first parameter to be '=': %s" % reply._s)
                self.assertEqual(reply.params[2], expect_channel, "Expected channel in NAMES to be %s: %s" % (expect_channel, reply._s))

        if expect_names is not None:
            names = reply.params[3][1:].split(" ")
            self.assertEqual(len(names), len(expect_names), "Expected list of names to have %i entries: %s" % (len(expect_names), reply._s))
            for name in expect_names:
                self.assertIn(name, names, "Expected %s in NAMES: %s" % (name, reply._s))        
        
    def _test_names(self, client, nick, expect_channel = None, expect_names = None):
        reply = self.get_reply(client, expect_code = replies.RPL_NAMREPLY, expect_nick = nick,
                               expect_nparams = 3)        
        self._test_names_single(reply, nick, expect_channel, expect_names)
            
        self.get_reply(client, expect_code = replies.RPL_ENDOFNAMES, expect_nick = nick,
                       expect_nparams = 2)        
    
        
    def _connect_user(self, nick, username):
        client = self.get_client()
        
        client.send_cmd("NICK %s" % nick)
        client.send_cmd("USER %s * * :%s" % (nick, username))
        
        self._test_welcome_messages(client, nick)
        self._test_lusers(client, nick)
        self._test_motd(client, nick)
        
        return client       
        

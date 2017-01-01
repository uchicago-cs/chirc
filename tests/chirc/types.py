import re



class CouldNotStartChircException(Exception):
    pass

class CouldNotConnectException(Exception):
    pass

class ServerDisconnectedException(Exception):
    pass

class ReplyTimeoutException(Exception):
    def __init__(self, bytes_received):
        self.bytes_received = bytes_received

class MessageNotWellFormedException(Exception):
    def __init__(self, reason, irc_msg):
        self.reason = reason
        self.irc_msg = irc_msg
        
    def __str__(self):
        return "{}\n\nMESSAGE: |||{}|||".format(self.reason, self.irc_msg)

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
            raise MessageNotWellFormedException("Message does not end in \\r\\n", s)
        
        self._s = s[:-2]
        
        if len(self._s) == 0:
            raise MessageNotWellFormedException("Entire message is just \\r\\n", s)
        
        fields = self._s.split(" ")
               
        if fields[0][0] == ":":
            if len(fields) == 1: 
                raise MessageNotWellFormedException("Message contains a prefix but no command.", s)
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
                
    def raw(self, bookends = False):
        if not bookends:
            return self._s
        else:
            return "|||{}|||".format(self._s)
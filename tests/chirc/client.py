import telnetlib
import time
from chirc.types import CouldNotConnectException, ReplyTimeoutException,\
    IRCMessage
import socket
            
class ChircClient(object):
    
    def __init__(self, host = "localhost", port = 7776, msg_timeout = 0.1, nodelay=False):
        self.host = host
        self.port = port
        self.msg_timeout = msg_timeout
        
        tries = 3

        while tries > 0:
            try:
                self.client = telnetlib.Telnet("localhost", str(self.port), 1)
                #self.client.set_debuglevel(100)
                if nodelay:
                    self.client.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                break
            except Exception:
                tries -= 1
                time.sleep(0.1)

        if tries == 0:
            raise CouldNotConnectException()
    
    def disconnect(self):
        self.client.close()
        
    def get_message(self):
        msg = self.client.read_until(str.encode("\r\n"), timeout=self.msg_timeout)
        msg = msg.decode()
        if msg[-2:] != "\r\n":
            raise ReplyTimeoutException(msg)
        msg = IRCMessage(msg)
        return msg

    def send_cmd(self, cmd):
        self.client.write(str.encode("%s\r\n" % cmd))
        
    def send_raw(self, l, wait = None):
        
        for s in l:
            if wait is not None:
                time.sleep(wait)
            self.client.write(str.encode(s))

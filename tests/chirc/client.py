import select
import socket
import time
from chirc.types import CouldNotConnectException, ReplyTimeoutException, IRCMessage


class ChircClient(object):

    def __init__(self, host="localhost", port=7776, msg_timeout=0.1, nodelay=False):
        self.host = host
        self.port = port
        self.msg_timeout = msg_timeout
        self._buf = b""

        tries = 3
        while tries > 0:
            try:
                self._sock = socket.create_connection((self.host, self.port), timeout=1)
                if nodelay:
                    self._sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                self._sock.settimeout(None)
                break
            except Exception:
                tries -= 1
                time.sleep(0.1)

        if tries == 0:
            raise CouldNotConnectException()

    def disconnect(self):
        self._sock.close()

    def get_message(self):
        deadline = time.monotonic() + self.msg_timeout
        while b"\r\n" not in self._buf:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                partial = self._buf.decode(errors="replace")
                self._buf = b""
                raise ReplyTimeoutException(partial)
            ready, _, _ = select.select([self._sock], [], [], remaining)
            if not ready:
                partial = self._buf.decode(errors="replace")
                self._buf = b""
                raise ReplyTimeoutException(partial)
            chunk = self._sock.recv(4096)
            if not chunk:
                raise EOFError()
            self._buf += chunk

        line, self._buf = self._buf.split(b"\r\n", 1)
        return IRCMessage((line + b"\r\n").decode())

    def send_cmd(self, cmd):
        self._sock.sendall(("%s\r\n" % cmd).encode())

    def send_raw(self, l, wait=None):
        for s in l:
            if wait is not None:
                time.sleep(wait)
            self._sock.sendall(s.encode())

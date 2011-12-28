import tests.replies as replies
import time
from tests.common import ChircTestCase, ChircClient

class FOO(ChircTestCase):

    def test_foo(self):
        self._connect_user("user1", "User One")
        

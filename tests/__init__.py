import unittest

import test_connection
import test_privmsg
import test_ping
import test_lusers_motd
import test_whois
import test_unknown
import test_channel

alltests = unittest.TestSuite([
                               unittest.TestLoader().loadTestsFromModule(test_connection),
                               unittest.TestLoader().loadTestsFromModule(test_privmsg),
                               unittest.TestLoader().loadTestsFromModule(test_ping),
                               unittest.TestLoader().loadTestsFromModule(test_lusers_motd),
                               unittest.TestLoader().loadTestsFromModule(test_whois),
                               unittest.TestLoader().loadTestsFromModule(test_unknown),
                               unittest.TestLoader().loadTestsFromModule(test_channel)
                               ])

DEBUG = False
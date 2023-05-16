import unittest

from powercmd.cmd import Cmd
from powercmd.command import Command


class TestCmd(unittest.TestCase):
    def test_get_all_commands(self):
        class TestImpl(Cmd):
            def do_test(self):
                pass

        expected_commands = {
            'exit': Command('exit', Cmd.do_exit),
            'EOF': Command('EOF', Cmd.do_EOF),
            'get_error': Command('get_error', Cmd.do_get_error),
            'help': Command('help', Cmd.do_help),
            'test': Command('test', TestImpl.do_test)
        }
        self.assertEqual(expected_commands, TestImpl()._get_all_commands())

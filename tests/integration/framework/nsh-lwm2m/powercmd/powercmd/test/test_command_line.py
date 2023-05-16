import unittest

from powercmd.command import Command, Parameter
from powercmd.command_line import CommandLine, NamedArg, PositionalArg, IncompleteArg
from powercmd.commands_dict import CommandsDict


class TestCommandLine(unittest.TestCase):
    def test_empty(self):
        cmdline = CommandLine('')
        self.assertEqual(cmdline.command, '')
        self.assertEqual(cmdline.args, [])
        self.assertEqual(cmdline.named_args, {})
        self.assertEqual(cmdline.free_args, [])
        self.assertEqual(cmdline.has_trailing_whitespace, False)

    def test_split_on_whitespace(self):
        cmdline = CommandLine('foo bar')
        self.assertEqual(cmdline.command, 'foo')
        self.assertEqual(cmdline.args, [PositionalArg('bar')])
        self.assertEqual(cmdline.named_args, {})
        self.assertEqual(cmdline.free_args, ['bar'])

        cmdline = CommandLine('foo\tbar')
        self.assertEqual(cmdline.command, 'foo')
        self.assertEqual(cmdline.args, [PositionalArg('bar')])
        self.assertEqual(cmdline.named_args, {})
        self.assertEqual(cmdline.free_args, ['bar'])

        cmdline = CommandLine('foo \tbar')
        self.assertEqual(cmdline.command, 'foo')
        self.assertEqual(cmdline.args, [PositionalArg('bar')])
        self.assertEqual(cmdline.named_args, {})
        self.assertEqual(cmdline.free_args, ['bar'])

    def test_positional_args(self):
        cmdline = CommandLine('foo bar baz')
        self.assertEqual(cmdline.command, 'foo')
        self.assertEqual(cmdline.args, [PositionalArg('bar'), PositionalArg('baz')])
        self.assertEqual(cmdline.named_args, {})
        self.assertEqual(cmdline.free_args, ['bar', 'baz'])

    def test_named_args(self):
        cmdline = CommandLine('foo bar=baz qux=quux')
        self.assertEqual(cmdline.command, 'foo')
        self.assertEqual(cmdline.args, [NamedArg('bar', 'baz'), NamedArg('qux', 'quux')])
        self.assertEqual(cmdline.named_args, {'bar': 'baz', 'qux': 'quux'})
        self.assertEqual(cmdline.free_args, [])

    def test_mixed_named_positional(self):
        cmdline = CommandLine('foo bar baz=qux')
        self.assertEqual(cmdline.command, 'foo')
        self.assertEqual(cmdline.args, [PositionalArg('bar'), NamedArg('baz', 'qux')])
        self.assertEqual(cmdline.named_args, {'baz': 'qux'})
        self.assertEqual(cmdline.free_args, ['bar'])

        cmdline = CommandLine('foo bar=baz qux')
        self.assertEqual(cmdline.command, 'foo')
        self.assertEqual(cmdline.args, [NamedArg('bar', 'baz'), PositionalArg('qux')])
        self.assertEqual(cmdline.named_args, {'bar': 'baz'})
        self.assertEqual(cmdline.free_args, ['qux'])

    def test_quoted_args(self):
        cmdline = CommandLine('foo "bar" \'baz\'')
        self.assertEqual(cmdline.command, 'foo')
        self.assertEqual(cmdline.args, [PositionalArg('bar'), PositionalArg('baz')])
        self.assertEqual(cmdline.named_args, {})
        self.assertEqual(cmdline.free_args, ['bar', 'baz'])

        cmdline = CommandLine('foo \'bar=baz\' "qux=quux"')
        self.assertEqual(cmdline.command, 'foo')
        self.assertEqual(cmdline.args, [NamedArg('bar', 'baz'), NamedArg('qux', 'quux')])
        self.assertEqual(cmdline.named_args, {'bar': 'baz', 'qux': 'quux'})
        self.assertEqual(cmdline.free_args, [])

    def test_command(self):
        self.assertEqual(CommandLine('foo').command, 'foo')

        self.assertEqual(CommandLine(' foo').command, 'foo')
        self.assertEqual(CommandLine('foo ').command, 'foo')

        self.assertEqual(CommandLine('"foo"').command, 'foo')
        self.assertEqual(CommandLine(' "foo"').command, 'foo')
        self.assertEqual(CommandLine('"foo" ').command, 'foo')

        self.assertEqual(CommandLine('" foo').command, '" foo')
        self.assertEqual(CommandLine('"foo ').command, '"foo ')

        self.assertEqual(CommandLine('" foo"').command, ' foo')
        self.assertEqual(CommandLine('"foo " ').command, 'foo ')

    def test_has_trailing_whitespace(self):
        self.assertEqual(CommandLine('foo ').has_trailing_whitespace, True)
        self.assertEqual(CommandLine('foo\t').has_trailing_whitespace, True)
        self.assertEqual(CommandLine('foo bar ').has_trailing_whitespace, True)
        self.assertEqual(CommandLine('foo bar\t').has_trailing_whitespace, True)
        self.assertEqual(CommandLine('foo bar=baz ').has_trailing_whitespace, True)
        self.assertEqual(CommandLine('foo bar=baz\t').has_trailing_whitespace, True)

        self.assertEqual(CommandLine('foo').has_trailing_whitespace, False)
        self.assertEqual(CommandLine('"foo"').has_trailing_whitespace, False)
        self.assertEqual(CommandLine('foo bar').has_trailing_whitespace, False)
        self.assertEqual(CommandLine('foo "bar"').has_trailing_whitespace, False)

        self.assertEqual(CommandLine('"foo ').has_trailing_whitespace, False)
        self.assertEqual(CommandLine('\'foo ').has_trailing_whitespace, False)
        self.assertEqual(CommandLine('foo "').has_trailing_whitespace, False)
        self.assertEqual(CommandLine('foo \'').has_trailing_whitespace, False)
        self.assertEqual(CommandLine('foo " ').has_trailing_whitespace, False)
        self.assertEqual(CommandLine('foo \' ').has_trailing_whitespace, False)
        self.assertEqual(CommandLine('foo "bar ').has_trailing_whitespace, False)
        self.assertEqual(CommandLine('foo \'bar ').has_trailing_whitespace, False)
        self.assertEqual(CommandLine('foo "bar=baz ').has_trailing_whitespace, False)
        self.assertEqual(CommandLine('foo \'bar=baz ').has_trailing_whitespace, False)

    def test_get_current_arg(self):
        def do_foo(self,
                   bar: str = '',
                   baz: str = ''):
            pass

        cmd = Command('foo', do_foo)

        self.assertEqual(CommandLine('').get_current_arg(cmd), None)
        self.assertEqual(CommandLine('foo').get_current_arg(cmd), None)
        self.assertEqual(CommandLine('foo ').get_current_arg(cmd),
                         IncompleteArg(Parameter('bar', str, ''), ''))
        self.assertEqual(CommandLine('foo arg').get_current_arg(cmd),
                         IncompleteArg(Parameter('bar', str, ''), 'arg'))
        self.assertEqual(CommandLine('foo arg ').get_current_arg(cmd),
                         IncompleteArg(Parameter('baz', str, ''), ''))
        self.assertEqual(CommandLine('foo arg arg').get_current_arg(cmd),
                         IncompleteArg(Parameter('baz', str, ''), 'arg'))
        self.assertEqual(CommandLine('foo baz=arg bar=').get_current_arg(cmd),
                         IncompleteArg(Parameter('bar', str, ''), ''))

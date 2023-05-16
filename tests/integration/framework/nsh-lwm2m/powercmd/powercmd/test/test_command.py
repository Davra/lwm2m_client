import inspect
import unittest

from powercmd.command import Command, Parameter


class CommandTest(unittest.TestCase):
    def test_parameters(self):
        def func(a: int, b: str = 'x'):
            pass

        cmd = Command(name='func', handler=func)
        self.assertEqual(cmd.parameters,
                         {'a': Parameter(name='a', type=int, default=inspect._empty),
                          'b': Parameter(name='b', type=str, default='x')})

    def test_short_description(self):
        def func():
            """
            Test function.

            Detailed description follows.
            """

        cmd = Command(name='func', handler=func)
        self.assertEqual(cmd.short_description, 'Test function.')

import unittest

from powercmd.split_list import split_list


class TestSplitList(unittest.TestCase):
    def test_empty(self):
        self.assertEqual([''], list(split_list('')))

    def test_single(self):
        self.assertEqual(['foo'], list(split_list('foo')))

    def test_multiple(self):
        self.assertEqual(['foo', 'bar'], list(split_list('foo,bar')))

    def test_parens(self):
        self.assertEqual(['(foo,bar)', '(baz,qux)'],
                         list(split_list('(foo,bar),(baz,qux)')))

    def test_nested_parens(self):
        self.assertEqual(['(foo,(bar,baz))', '(qux)'],
                         list(split_list('(foo,(bar,baz)),(qux)')))

    def test_mixed_delimiters(self):
        self.assertEqual(['(foo,"bar[baz]",{\'qux\'})', 'ggg'],
                         list(split_list('(foo,"bar[baz]",{\'qux\'}),ggg')))

    def test_custom_separator(self):
        self.assertEqual(['foo', 'bar'],
                         list(split_list('foo|bar', separator='|')))

    def test_unmatched_paren(self):
        with self.assertRaises(ValueError):
            list(split_list('(foo,bar'))

    def test_unmatched_paren_allowed(self):
        self.assertEqual(['(foo,bar'],
                         list(split_list('(foo,bar', allow_unmatched=True)))

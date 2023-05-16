"""
Utilities for matching sloppily written commands to existing ones.
"""

import os
from typing import Callable, List, Sequence, Tuple


class TextMatchStrategy:
    """
    Represents a method of checking if given text matches a pattern.
    """
    def __init__(self,
                 name: str,
                 matcher: Callable[[str, str], bool]):
        self.name = name
        self.matcher = matcher

    def __call__(self,
                 text: str,
                 pattern: str) -> bool:
        return self.matcher(text, pattern)

    @staticmethod
    def _prefixes_of(text: str) -> Sequence[str]:
        """
        Returns all prefixes if given TEXT including itself, longest first.
        """
        for i in range(len(text)):
            yield text[i:]

    @staticmethod
    def _matches_words(text: str,
                       words: Sequence[str]) -> bool:
        """
        Returns true if given TEXT can be assembled from non-empty prefixes of
        WORDS in order.

        Examples:
            _matches_words("po", ["prefixes", "of"]) => True
            _matches_words("gval", ["get", "value"]) => True
            _matches_words("gv", ["get", "total", "value", "of", "xs"]) => False
            _matches_words("st", ["set", "foo"]) => False
        """
        if not text:
            return True

        for word in words:
            common_prefix = os.path.commonprefix([text, word])
            if not common_prefix:
                return False
            if common_prefix == text:
                return True

            for prefix in TextMatchStrategy._prefixes_of(common_prefix):
                if TextMatchStrategy._matches_words(text[len(prefix):],
                                                    words[1:]):
                    return True
        return False

    @staticmethod
    def snake_case_matches(short: str,
                           full: str) -> bool:
        """
        Checks if SHORT is an abbreviation of FULL snake-case text.

        Examples:
            snake_case_matches("po", "prefixes_of") => True
            snake_case_matches("gval", "get_value") => True
            snake_case_matches("gv", "get_total_value_of_foo") => False
            snake_case_matches("st", "set_foo") => False
        """
        return TextMatchStrategy._matches_words(short, full.split('_'))

    @staticmethod
    def fuzzy_matches(short: str,
                      full: str) -> bool:
        """
        Checks if FULL contains all elements of SHORT in the same order. That
        does not mean that SHORT == FULL - FULL can contain other elements not
        present in SHORT.
        """
        short_at = 0
        for char in full:
            if char == short[short_at]:
                short_at += 1
                if short_at == len(short):
                    return True
        return False


TextMatchStrategy.Exact = \
        TextMatchStrategy('exact', lambda a, b: a == b)
TextMatchStrategy.Prefix = \
        TextMatchStrategy('prefix', lambda short, full: full.startswith(short))
TextMatchStrategy.SnakeCase = \
        TextMatchStrategy('snake case', TextMatchStrategy.snake_case_matches)
TextMatchStrategy.Fuzzy = \
        TextMatchStrategy('fuzzy', TextMatchStrategy.fuzzy_matches)


def _match_string(text: str,
                  possible: List[str],
                  match_strategies: Sequence[Tuple[str, Callable[[str, str], bool]]],
                  verbose: bool) -> List[str]:
    """
    Attempts to match TEXT to one of POSSIBLE, using multiple MATCH_STRATEGIES.
    Returns after any of MATCH_STRATEGIES finds some matches, i.e. the return
    value will always contain elements matched using the same strategy.

    Prints the name of successful strategy unless QUIET is set to True.

    Returns the list of matches sorted in alphabetical order.
    """
    for match in match_strategies:
        matches = sorted([e for e in possible if match(text, e)])
        if matches:
            if verbose:
                print('* %s: %s' % (match.name, ' '.join(matches)))
            return matches

    return []


def simple_match_string(text, possible):
    """
    Returns subset of POSSIBLE commands matching TEXT using simple match
    strategies (exact or prefix match).
    """
    match_strategies = [
        TextMatchStrategy.Exact,
        TextMatchStrategy.Prefix
    ]
    return _match_string(text, list(possible), match_strategies, verbose=True)


def match_string(text, possible, verbose=False):
    """
    Returns subset of POSSIBLE commands matching TEXT using all available
    match strategies (exact/prefix/snake case/fuzzy match).
    """
    match_strategies = [
        TextMatchStrategy.Exact,
        TextMatchStrategy.Prefix,
        TextMatchStrategy.SnakeCase,
        TextMatchStrategy.Fuzzy
    ]
    return _match_string(text, list(possible), match_strategies, verbose=verbose)

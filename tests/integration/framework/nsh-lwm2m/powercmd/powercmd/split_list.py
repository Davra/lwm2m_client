"""
Utility function for splitting a string into list of elements.
"""

from typing import Callable, List, Mapping


def _split(text: str,
           is_separator: Callable[[str], bool],
           delimiters: Mapping[str, str],
           allow_unmatched: bool = False,
           collapse_separators: bool = False) -> List[str]:
    """
    Splits TEXT on characters for which IS_SEPARATOR returns true, preserving
    separators inside nested pairs of DELIMITERS.

    If ALLOW_UNMATCHED is False, an exception is thrown if delimiters are
    unbalanced.
    """
    if any(is_separator(c) for c in delimiters):
        raise ValueError('delimiters: %s are not supported as separators'
                         % (''.join(delimiters),))

    stack = []
    start = 0

    for idx, char in enumerate(text):
        if stack:
            if stack[-1] == char:
                stack.pop()
        elif char in delimiters:
            stack.append(delimiters[char])
        elif is_separator(char):
            yield text[start:idx]
            start = idx + 1

    if not allow_unmatched and stack:
        raise ValueError('text contains unmatched delimiters: %s (text = %s)'
                         % (''.join(stack), text))

    yield text[start:]


def split_list(text: str,
               separator: str = ',',
               allow_unmatched: bool = False) -> List[str]:
    """
    Splits TEXT on SEPARATOR, preserving SEPARATOR nested inside pairs of
    parens, brackets, braces and quotes.

    If ALLOW_UNMATCHED is False, an exception is thrown if the parens/quotes
    are unbalanced.
    """

    if len(separator) != 1:
        raise ValueError('only single-character separators are supported')

    _DELIMITERS = {
        '(': ')',
        '[': ']',
        '{': '}',
        '"': '"',
        "'": "'",
    }

    return list(_split(text, (lambda c: c == separator), _DELIMITERS, allow_unmatched))


_QUOTES = {
    '"': '"',
    "'": "'",
}


def split_cmdline(text: str,
                  allow_unmatched: bool = False) -> List[str]:

    cmdline_words = list(_split(text, str.isspace, _QUOTES, allow_unmatched))

    # collapse consecutive whitespace
    cmdline_words = [word for word in cmdline_words if word]

    return cmdline_words


def drop_enclosing_quotes(word: str) -> str:
    if len(word) > 1 and word[0] in _QUOTES and word[-1] == _QUOTES[word[0]]:
        return word[1:-1]
    return word

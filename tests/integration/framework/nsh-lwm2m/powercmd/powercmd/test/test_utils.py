import collections
import inspect
from typing import Callable

ProxyCall = object()
MockCall = collections.namedtuple('Call', ['args', 'kwargs', 'retval'])


class CallWrapper(object):
    def __init__(self,
                 fn: Callable,
                 static: bool = False):
        self.fn = fn
        self.static = static
        self.calls = []

    def __enter__(self):
        pass

    def __exit__(self, *exc):
        if not exc[0] and len(self.calls) != 0:
            raise AssertionError('%d more calls expected' % len(self.calls))

    def expect_no_calls(self):
        return self

    def expect_call(self, *args, **kwargs):
        self.calls.insert(0, MockCall(args, kwargs, ProxyCall))
        return self

    def returning(self, retval):
        self.calls[0].retval = retval
        return self

    def __getattr__(self, attr):
        return getattr(self.fn, attr)

    @property
    def __signature__(self):
        return inspect.signature(self.fn)

    def __call__(self, *args, **kwargs):
        if len(self.calls) == 0:
            raise AssertionError('unexpected call with %s' % (repr(kwargs),))

        call = self.calls.pop(0)

        actual_args = args if self.static else args[1:]

        if call.args != actual_args:
            raise AssertionError('expected call with positional args: %s, got %s'
                                 % (repr(call.args), repr(args)))
        if call.kwargs != kwargs:
            raise AssertionError('expected call with named args: %s, got %s'
                                 % (repr(call.kwargs), repr(kwargs)))
        if call.retval is ProxyCall:
            if self.static:
                return self.fn.__func__(*args, **kwargs)
            else:
                return self.fn(*args, **kwargs)
        else:
            return call.retval

    def __str__(self):
        def stringify_call(call):
            return ('call: %s -> %s'
                    % (' '.join('='.join((k, repr(v)))
                                for k, v in call.args.items()),
                       '<proxy call>' if call.retval is ProxyCall else repr(call.retval)))

        return ('%d calls:\n%s'
                % (len(self.calls),
                   '\n'.join(stringify_call(call) for call in self.calls)))


def mock(fn):
    return CallWrapper(fn)


def static_mock(fn):
    return CallWrapper(fn, static=True)

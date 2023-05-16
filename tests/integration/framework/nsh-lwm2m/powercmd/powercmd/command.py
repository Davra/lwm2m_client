"""
Utility classes for accessing type hints of function arguments.
"""

import collections
import inspect
import textwrap

from powercmd.extra_typing import OrderedMapping


class Parameter(collections.namedtuple('Parameter', ['name', 'type', 'default'])):
    """
    Type-annotated function parameter.
    """
    def __new__(cls, *args, **kwargs):
        param = super().__new__(cls, *args, **kwargs)
        if param.type == inspect._empty:  # pylint: disable=protected-access
            raise ValueError('Type not specified for paramter %s' % param.name)
        return param

    def __str__(self):
        # TODO: check if type is Optional[x], print None in such case
        result = '%s: %s' % (self.name, self.type)
        if self.default is not None:
            result += ' = %s' % repr(self.default)
        return result


class Command(collections.namedtuple('Command', ['name', 'handler'])):
    """
    Command handler: a powercmd.Cmd method with non-self parameters annotated
    with type hints.
    """
    def __new__(cls, *args, **kwargs):
        cmd = super().__new__(cls, *args, **kwargs)
        cmd.get_parameters()
        return cmd

    def _get_handler_params(self) -> OrderedMapping[str, inspect.Parameter]:
        """Returns a list of command parameters for given HANDLER."""
        params = inspect.signature(self.handler).parameters
        params = list(params.items())
        if params and params[0][0] == 'self':
            params = params[1:]  # drop 'self'
        params = collections.OrderedDict(params)  # drop 'self'
        return params

    def get_parameters(self) -> OrderedMapping[str, Parameter]:
        """Returns an OrderedDict of command parameters."""
        try:
            params = self._get_handler_params()
            return collections.OrderedDict((name, Parameter(name=name,
                                                            type=param.annotation,
                                                            default=param.default))
                                           for name, param in params.items())
        except ValueError as exc:
            raise ValueError('Unable to list parameters for handler: %s' % self.name) from exc

    @property
    def parameters(self) -> OrderedMapping[str, Parameter]:
        """Returns an OrderedDict of command parameters."""
        return self.get_parameters()

    @property
    def description(self) -> str:
        """Returns command handler docstring."""
        return self.handler.__doc__

    @property
    def short_description(self) -> str:
        """Returns the first line of command handler docstring."""
        if self.description is not None:
            return self.description.strip().split('\n', maxsplit=1)[0]
        return None

    def _param_to_help_str(self, param) -> str:
        """Returns the help string for the given param name"""
        if self.parameters[param].default is inspect.Parameter.empty:
            return str(param)
        else:
            return str(param) + '?'

    @property
    def help(self) -> str:
        """Returns a help message for this command handler."""
        return ('%s\n\nARGUMENTS: %s %s\n'
                % (textwrap.dedent(self.description or 'No details available.').strip(),
                   self.name,
                   ' '.join(self._param_to_help_str(param) for param in self.parameters)))

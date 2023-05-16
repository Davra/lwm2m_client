"""
Utilities for constructing command arguments.
"""

import collections
import copy
import enum
import inspect
from typing import Any, Callable, List, Mapping, Sequence, Tuple, Union, Optional

from powercmd.command_line import CommandLine, MISSING_ARG
from powercmd.commands_dict import CommandsDict
from powercmd.exceptions import InvalidInput
from powercmd.extra_typing import OrderedMapping
from powercmd.split_list import split_list
from powercmd.utils import (is_generic_list, is_generic_tuple, is_generic_type,
                            is_generic_union)


class CommandInvoker:
    """
    Constructs command handler arguments and invokes appropriate handler with
    constructed argumnds.
    """
    def __init__(self, commands: CommandsDict):
        self._cmds = commands

    @staticmethod
    def _get_list_ctor(annotation: List) -> Callable[[str], List]:
        """
        Returns a function that parses a string representation of a list
        defined by ANNOTATION.

        Examples:
            "[1,2,3]" -> List[int]
            "1,2,3" -> List[int]
        """
        if len(annotation.__args__) != 1:
            raise TypeError('List may only have one type parameter, got %s'
                            % (annotation,))
        internal_type = annotation.__args__[0]
        internal_ctor = CommandInvoker.get_constructor(internal_type)

        def construct_list(text):
            if text[0] == '[' and text[-1] == ']':
                text = text[1:-1]
            return [internal_ctor(txt) for txt in split_list(text)]

        return construct_list

    @staticmethod
    def _get_tuple_ctor(annotation: Tuple) -> Callable[[str], Tuple]:
        """
        Returns a function that parses a string representation of a tuple
        defined by ANNOTATION.

        Examples:
            "(1,foo)" -> Tuple[int, str]
        """
        internal_types = getattr(annotation, '__args__', None)
        if internal_types is None:
            raise TypeError('%s is not a tuple type' % (repr(annotation),))

        def construct_tuple(text):
            if text[0] == '(' and text[-1] == ')':
                text = text[1:-1]

            sub_txts = list(split_list(text))
            if len(sub_txts) != len(internal_types):
                raise TypeError('mismatched lengths: %d strings, %d tuple types' % (len(sub_txts), len(internal_types)))

            tuple_list = []
            for cls, txt in zip(internal_types, sub_txts):
                tuple_list.append(CommandInvoker.get_constructor(cls)(txt))

            return tuple(tuple_list)

        return construct_tuple

    @staticmethod
    def _get_union_ctor(annotation: Union):
        """
        Returns a function that parses a string into the first matching type of
        ANNOTATION.
        """
        internal_types = (getattr(annotation, '__args__', None)
                          or getattr(annotation, '__union_types__', None))
        if internal_types is None:
            raise TypeError('%s is not a union type' % (repr(annotation),))

        def construct_union(text):
            for internal_type in internal_types:
                ctor = CommandInvoker.get_constructor(internal_type)
                try:
                    return ctor(text)
                except ValueError:
                    pass

        return construct_union

    @staticmethod
    def get_constructor(annotation: Any) -> Callable[[str], Any]:
        """
        Returns a callable that parses a string and returns an object of an
        appropriate type defined by the ANNOTATION.
        """
        def ensure_callable(arg):
            """Raises an exception if the argument is not callable."""
            if not callable(arg):
                raise TypeError('invalid type: ' + repr(arg))
            return arg

        if is_generic_type(annotation):
            return CommandInvoker.get_generic_constructor(annotation)
        if issubclass(annotation, enum.Enum):
            # Enum class allows accessing values by string via [] operator
            return annotation.__getitem__
        if hasattr(annotation, 'powercmd_parse'):
            return getattr(annotation, 'powercmd_parse')

        if annotation is bool:
            # Booleans are actually quite special. In python bool(nonempty seq)
            # is always True, therefore if used verbatim, '0' would evaluate to
            # True, which, if you ask me, looks highly counter-intuitive.
            return lambda value: value not in ('', '0', 'false', 'False')

        return {
            bytes: lambda text: bytes(text, 'ascii'),
        }.get(annotation, ensure_callable(annotation))

    @staticmethod
    def get_generic_constructor(annotation: Any) -> Callable[[str], Any]:
        """
        Returns a function that constructs a generic type from given string.
        It is used for types like List[Foo] to apply a Foo constructor for each
        list element.
        """
        if is_generic_list(annotation):
            return CommandInvoker._get_list_ctor(annotation)
        if is_generic_tuple(annotation):
            return CommandInvoker._get_tuple_ctor(annotation)
        if is_generic_union(annotation):
            return CommandInvoker._get_union_ctor(annotation)

        raise NotImplementedError('generic constructor for %s not implemented'
                                  % (annotation,))

    @staticmethod
    def _construct_arg(formal_param: inspect.Parameter,
                       value: str) -> Any:
        """
        Constructs an argument from string VALUE, with the type defined by an
        annotation to the FORMAL_PARAM.
        """
        ctor = CommandInvoker.get_constructor(formal_param.type)
        try:
            return ctor(value)
        except ValueError as exc:
            raise InvalidInput(exc)

    @staticmethod
    def _fill_default_args(formal: Mapping[str, inspect.Parameter],
                           actual: Mapping[str, str]):
        """
        Returns the ACTUAL dict extended by default values of unassigned FORMAL
        parameters.
        """
        result = copy.copy(actual)
        for name, param in formal.items():
            if (name not in result
                    and param.default is not inspect.Parameter.empty):
                result[name] = param.default

        return result

    @staticmethod
    def _construct_args(formal: Mapping[str, inspect.Parameter],
                        assigned_args: Mapping[str, str]) -> Mapping[str, Any]:
        """
        Construct FORMAL args from ASSIGNED_ARGS and defaults.
        """
        constructed_args = {}

        for name, value in assigned_args.items():
            if name in constructed_args:
                raise InvalidInput('duplicate value for argument: %s' % (name,))

            if value is MISSING_ARG:
                if formal[name].default is inspect.Parameter.empty:
                    raise InvalidInput('missing value for argument: %s' % (name,))
            else:
                constructed_args[name] = CommandInvoker._construct_arg(formal[name], value)

        constructed_args = CommandInvoker._fill_default_args(formal, constructed_args)
        return constructed_args

    def invoke(self,
               *args,
               cmdline: CommandLine):
        """
        Parses CMDLINE and invokes appropriate command handler. Any additional
        ARGS are passed to the handler.
        """
        cmd = self._cmds.choose(cmdline.command, verbose=True)
        assigned_args = cmdline.assign_args(cmd)
        typed_args = self._construct_args(cmd.parameters, assigned_args)

        return cmd.handler(*args, **typed_args)

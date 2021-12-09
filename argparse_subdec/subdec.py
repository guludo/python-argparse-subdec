# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
from __future__ import annotations

import argparse
import collections.abc as C
import typing as ty


F = ty.TypeVar('F', bound=ty.Callable[..., ty.Any])


Decorator = ty.Callable[[F], F]


DecoratorFactory = ty.Callable[..., Decorator[F]]


AnyCallable = ty.Callable[..., ty.Any]


AnyDecoratorFactory = DecoratorFactory[AnyCallable]


class CommandDescriptor(ty.TypedDict):
    name: ty.Optional[str]
    fn: AnyCallable
    subparser_call_stack: ty.List[SubparserCallDescriptor]
    add_parser_args: ty.Optional[ty.Tuple[ty.Sequence[ty.Any],
                                          ty.Dict[str, ty.Any]]]

class SubparserCallDescriptor(ty.TypedDict):
    method_name: str
    args: ty.Tuple[ty.Any, ...]
    kwargs: ty.Dict[str, ty.Any]


class SubparsersProtocol(ty.Protocol):
    """
    A protocol class to describe the returned value of
    ``argparse.ArgumentParser.add_subparsers()``, since the official
    documentation does not point to a public type for the returned value.
    """
    def add_parser(self, name: str, **kw: ty.Any) -> argparse.ArgumentParser:
        ... # pragma: no cover


class SubDec:
    """
    This class provides a way to decorate functions as subcommands for
    argparse.

    It provides an implementation of `__getattr__` that allows one to annotate
    a function (which represents a subcommand) multiple times as if calling
    methods on a sub-parser for that command.

    The example below creates two subcommands::

    >>> sd = SubDec()

    >>> @sd.add_argument('--option', default='123')
    ... @sd.add_argument('--another')
    ... def foo(args):
    ...     print(f'foo subcommand: --option={args.option!r} and --another={args.another!r}')

    >>> @sd.cmd(prefix_chars=':')
    ... @sd.add_argument('positional_arg', type=int)
    ... def foo_bar(args):
    ...     print(f'foo-bar subcommand: {args.positional_arg!r}')

    Note that the second command uses a special decorator ``cmd()``, which
    passes all of its arguments down to ``add_parser()`` when creating the
    sub-parser.

    In order to create the sub-parsers, you must call ``sd.create_parsers()``
    passing a ``subparsers`` object as argument::

    >>> parser = argparse.ArgumentParser()
    >>> subparsers = parser.add_subparsers()
    >>> sd.create_parsers(subparsers)

    >>> args = parser.parse_args(['foo', '--another', 'hello'])

    By default, the subcommand function is assigned to ``args.fn``::

    >>> args.fn(args)
    foo subcommand: --option='123' and --another='hello'

    Calling the second command::

    >>> args = parser.parse_args(['foo-bar', '42'])
    >>> args.fn(args)
    foo-bar subcommand: 42
    """

    def __init__(self,
        name_prefix: str = '',
        fn_dest: str = 'fn',
        sep: str = '-',
    ):
        """
        Initialize this object.

        If ``name_prefix`` is not empty, that prefix is removed from the
        function name when defining the name of that function's subparser.

        The parameter ``fn_dest`` (default: "fn") defines the name of the
        attribute in the object returned by ``parse_args()`` the decorated
        function will be assigned to.

        The parameter ``sep`` (default: "-") defines the string that will
        replace the underscore character ("_") when converting the name of the
        decorated function to a subcommand name.
        """
        self.__decorators_cache: ty.Dict[str, AnyDecoratorFactory] = {}
        self.__commands: ty.Dict[AnyCallable, CommandDescriptor] = {}
        self.__name_prefix = name_prefix
        self.__fn_dest = fn_dest
        self.__sep = sep

    def create_parsers(self, subparsers: SubparsersProtocol) -> None:
        """
        Create subparsers by calling ``subparsers.add_parser()`` for each
        decorated function.
        """
        for cmd in self.__commands.values():
            self.__create_parser(cmd, subparsers)

    def cmd(self, *k: ty.Any, **kw: ty.Any) -> DecoratorFactory[F]:
        """
        Special decorator to register arguments to be passed do
        ``add_parser()``.
        """
        def decorator(fn: F) -> F:
            cmd = self.__get_command(fn)
            cmd['add_parser_args'] = (k, kw)
            return fn
        return decorator

    def __getattr__(self, name: str) -> AnyDecoratorFactory:
        if name in self.__decorators_cache:
            return self.__decorators_cache[name]

        def decorator_wrapper(*k: ty.Any, **kw: ty.Any) -> Decorator[F]:
            def decorator(fn: F) -> F:
                cmd = self.__get_command(fn)
                cmd['subparser_call_stack'].append({
                    'method_name': name,
                    'args': k,
                    'kwargs': kw,
                })
                return fn
            return decorator

        self.__decorators_cache[name] = decorator_wrapper
        return decorator_wrapper

    def __get_command(self, fn: AnyCallable) -> CommandDescriptor:
        if fn not in self.__commands:
            self.__commands[fn] = {
                'name': None,
                'fn': fn,
                'subparser_call_stack': [],
                'add_parser_args': None,
            }
        return self.__commands[fn]

    def __create_parser(self,
                        cmd: CommandDescriptor,
                        subparsers: SubparsersProtocol,
                        ) -> None:
        name = cmd['name']
        if not name:
            name = cmd['fn'].__name__
            if name.startswith(self.__name_prefix):
                name = name[len(self.__name_prefix):]
            if self.__sep is not None:
                name = name.replace('_', self.__sep)

        if cmd['add_parser_args'] is not None:
            add_parser_args, add_parser_kwargs = cmd['add_parser_args']
            if not add_parser_args:
                add_parser_args = (name,)
        else:
            add_parser_args = (name,)
            add_parser_kwargs = {}

        parser = subparsers.add_parser(*add_parser_args, **add_parser_kwargs)
        parser.set_defaults(**{self.__fn_dest: cmd['fn']})

        for call_data in reversed(cmd['subparser_call_stack']):
            method = getattr(parser, call_data['method_name'])
            method(*call_data['args'], **call_data['kwargs'])

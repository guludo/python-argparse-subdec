python-argparse-subdec
######################

This is a very simple Python package that allows one to create argparse_'s
subcommands via function decorators.

Usage
=====

Create a ``SubDec`` object:

.. code:: python

  import argparse_subdec

  # Create the object to collect subcommands via decorators
  sd = argparse_subdec.SubDec()

Now, we can define our subcommands. We define a subcommand by decorating a
function with method calls to ``sd``, like below:

.. code:: python

  @sd.add_argument('--option', default='123')
  @sd.add_argument('--another')
  def foo(args):
      print(f'foo subcommand: --option={args.option!r} and --another={args.another!r}')

You can use any method name that you would use in a subparser. In our example
above, we used ``add_argument``, probably most commonly used. When creating
the subparsers, ``sd`` will replay those calls to the created subparser for
the ``foo`` subcommand.


In the example below we define a second subcommand, which will be named
``foo-bar``:

.. code:: python

  @sd.cmd(prefix_chars=':')
  @sd.add_argument('positional_arg', type=int)
  def foo_bar(args):
      print(f'foo-bar subcommand: {args.positional_arg!r}')

Note that we use a special decorator, ``sd.cmd``, which makes ``sd`` pass all
of its arguments down to ``add_parser()`` when creating the subparser for
``foo-bar``.

Once our subcommands are defined, we must call ``sd.create_parsers()`` in
order to effectively create the subparsers:

.. code:: python

  parser = argparse.ArgumentParser()
  subparsers = parser.add_subparsers()
  sd.create_parsers(subparsers)


The following is example of how we would call the subcommands:

.. code:: python

    args = parser.parse_args(['foo', '--another', 'hello'])
    args.fn(args) # The subcommand function is assigned to ``args.fn`` by default
    # Outputs: foo subcommand: --option='123' and --another='hello'


For more details about the API, check out the subdec_ module.


Install
=======

Via ``pip``:

.. code:: bash

   pip install argparse-subdec


.. _argparse: https://docs.python.org/3/library/argparse.html
.. _subdec: argparse_subdec/subdec.py

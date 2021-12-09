import argparse

import argparse_subdec


def test_command_decorator() -> None:
    sd = argparse_subdec.SubDec()

    @sd.cmd()
    def foo() -> None:
        pass

    @sd.cmd()
    def two_words() -> None:
        pass

    @sd.add_argument('--option-for-bar')
    @sd.add_argument('--another-option-for-bar')
    def bar() -> None:
        pass

    @sd.cmd('changed-name')
    @sd.add_argument('--option')
    def original_name() -> None:
        pass

    # Test changing order of decorators
    @sd.add_argument('--option')
    @sd.cmd('changed-name-2')
    def another_original_name() -> None:
        pass

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    sd.create_parsers(subparsers)

    args = parser.parse_args(['foo'])
    expected_args = argparse.Namespace(
        fn=foo,
    )
    assert args == expected_args

    args = parser.parse_args(['two-words'])
    expected_args = argparse.Namespace(
        fn=two_words,
    )
    assert args == expected_args

    args = parser.parse_args(['bar', '--option-for-bar', 'hello'])
    expected_args = argparse.Namespace(
        fn=bar,
        option_for_bar='hello',
        another_option_for_bar=None,
    )
    assert args == expected_args

    args = parser.parse_args(['changed-name', '--option', 'hello'])
    expected_args = argparse.Namespace(
        fn=original_name,
        option='hello',
    )
    assert args == expected_args

    args = parser.parse_args(['changed-name-2'])
    expected_args = argparse.Namespace(
        fn=another_original_name,
        option=None,
    )
    assert args == expected_args

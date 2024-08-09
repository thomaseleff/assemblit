""" Command-line utility """

import sys
import errno
import argparse
from assemblit.app.cli import commands


# Define assemblit CLI tool function(s)
def main():
    """
    usage: assemblit [-h] {run} ...

    CLI application for building and running `assemblit` web-applications.

    options:
    -h, --help  Show this help message and exit

    commands:
    The web-application command options.

    {build, run}
        build      Builds a new project.
        run        Runs a local Python script.

    Execute `assemblit {command} --help` for help.
    """

    # Setup CLI argument option(s)
    _ARG_PARSER = argparse.ArgumentParser(
        prog='assemblit',
        description='CLI application for building and running `assemblit` web-applications.',
        epilog="Execute `assemblit {command} --help` for more help."
    )

    # Setup command argument option(s)
    _ARG_SUBPARSER = _ARG_PARSER.add_subparsers(
        title='commands',
        prog='assemblit',
        description='The `assemblit` command options.'
    )

    # Setup `build` command CLI argument option(s)
    _BUILD_ARG_PARSER = _ARG_SUBPARSER.add_parser(
        name='build',
        help='Builds a new project.',
        epilog="Execute `assemblit build --help` for help."
    )
    _BUILD_ARG_PARSER.add_argument(
        'app_type',
        help="The type of web-application.",
        type=str,
        choices=['demo']
    )
    _BUILD_ARG_PARSER.set_defaults(func=commands.build)

    # Setup `run` command CLI argument option(s)
    _RUN_ARG_PARSER = _ARG_SUBPARSER.add_parser(
        name='run',
        help='Runs a local Python script.',
        epilog="Execute `assemblit run --help` for help."
    )
    _RUN_ARG_PARSER.add_argument(
        'script',
        help="The relative or absolute path to a local Python script.",
        type=str
    )
    _RUN_ARG_PARSER.set_defaults(func=commands.run)

    # Parse arguments
    _ARGS = _ARG_PARSER.parse_args()
    _KWARGS = {key: vars(_ARGS)[key] for key in vars(_ARGS).keys() if key != 'func'}

    # Execute sub-command
    if _ARG_PARSER.parse_args():
        _ARGS.func(**_KWARGS)
    else:
        return errno.EINVAL


if __name__ == '__main__':
    sys.exit(main())

""" Workflow orchestrator """

import sys
import errno
import argparse
from assemblit.orchestrator.cli import commands


# Define orchestrator CLI tool function(s)
def main():
    """
    usage: orchestrator [-h] {start} ...

    CLI application for starting, managing and interacting with the
    orchestration server.

    options:
    -h, --help  Show this help message and exit

    commands:
    The orchestration server command options.

    {start}
        start     Starts the workflow orchestration server.

    Execute `orchestrator {command} --help` for help.
    """

    # Setup CLI argument option(s)
    _ARG_PARSER = argparse.ArgumentParser(
        prog='orchestrator',
        description='CLI application for starting, managing and interacting with the orchestration server.',
        epilog="Execute `orchestrator {command} --help` for more help."
    )

    # Setup `start` command CLI argument option(s)
    _ARG_SUBPARSER = _ARG_PARSER.add_subparsers(
        title='commands',
        prog='orchestrator',
        description='The orchestration server command options.'
    )
    _START_ARG_PARSER = _ARG_SUBPARSER.add_parser(
        name='start',
        help='Starts the workflow orchestration server.',
        epilog="Execute `orchestrator start --help` for help."
    )
    _START_ARG_PARSER.add_argument(
        'path',
        help="The relative or absolute path to the current work-directory.",
        type=str
    )
    _START_ARG_PARSER.set_defaults(func=commands.start)

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

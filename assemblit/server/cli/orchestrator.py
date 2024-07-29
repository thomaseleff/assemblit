"""
Information
---------------------------------------------------------------------
Name        : orchestrator.py
Location    : ~/server/cli

Description
---------------------------------------------------------------------
usage: orchestrator [-h] {start} ...

CLI application for starting, mnanaging and interacting with the
orchestration server.

options:
  -h, --help  Show this help message and exit

subcommands:
  The orchestration server command options.

  {start}
    start     The orchestration server start command.

Execute `orchestrator {subcommand} --help` for help.
"""

import sys
import errno
import argparse
from assemblit.server import layer
from assemblit.server.cli import commands


# Define orchestrator CLI tool function(s)
def main():

    # Setup CLI argument option(s)
    _ARG_PARSER = argparse.ArgumentParser(
        prog='orchestrator',
        description='CLI application for starting, mnanaging and interacting with the orchestration server.',
        epilog="Execute `orchestrator {subcommand} --help` for more help."
    )

    # Setup `start` command CLI argument option(s)
    _ARG_SUBPARSER = _ARG_PARSER.add_subparsers(
        prog='orchestrator',
        description='The orchestration server command options.'
    )
    _START_ARG_PARSER = _ARG_SUBPARSER.add_parser(
        name='start',
        help='The orchestration server start command.',
        epilog="Execute `orchestrator start --help` for help."
    )
    _START_ARG_PARSER.add_argument(
        '-N',
        '--server_name',
        help="The name of the orchestration server.",
        type=str,
        required=True
    )
    _START_ARG_PARSER.add_argument(
        '-T',
        '--server_type',
        help=''.join([
            "The type of the orchestration server.",
            " Currently, `assemblit` supports the following orchestration server types, [%s]." % (
                ', '.join(["'%s'" % (i.strip().lower()) for i in layer._SERVER_TYPES])
            )
        ]),
        choices=layer._SERVER_TYPES,
        type=str,
        required=True
    )
    _START_ARG_PARSER.add_argument(
        '-P',
        '--server_port',
        help="The registered port address of the orchestration server.",
        type=str,
        required=True
    )
    _START_ARG_PARSER.add_argument(
        '-D',
        '--root_dir',
        help="Local directory path of the orchestration server data.",
        type=str,
        required=True
    )
    _START_ARG_PARSER.add_argument(
        '-E',
        '--job_entrypoint',
        help="The `python` program containing the job definition and deploy proceedure.",
        type=str,
        required=True
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

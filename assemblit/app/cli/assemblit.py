""" Assemblit CLI-tool

usage: assemblit [-h] {run} ...

CLI application for building and running `assemblit` web-applications.

options:
  -h, --help  Show this help message and exit

subcommands:
  The web-application command options.

  {run}
    run     The web-application run command.
    build   The web-application build command.

Execute `assemblit {subcommand} --help` for help.
"""

import sys
import errno
import argparse
from assemblit.app import layer
from assemblit.app.cli import commands


# Define assemblit CLI tool function(s)
def main():

    # Setup CLI argument option(s)
    _ARG_PARSER = argparse.ArgumentParser(
        prog='assemblit',
        description='CLI application for building and running `assemblit` web-applications.',
        epilog="Execute `assemblit {subcommand} --help` for more help."
    )

    # Setup `run` command CLI argument option(s)
    _ARG_SUBPARSER = _ARG_PARSER.add_subparsers(
        prog='assemblit',
        description='The assemblit command options.'
    )
    _RUN_ARG_PARSER = _ARG_SUBPARSER.add_parser(
        name='run',
        help='The assemblit run command.',
        epilog="Execute `assemblit run --help` for help."
    )
    _RUN_ARG_PARSER.add_argument(
        '-T',
        '--app_type',
        help=''.join([
            "The type of the assemblit web-application.",
            " Currently, `assemblit` supports the following web-application types, [%s]." % (
                ', '.join(["'%s'" % (i.strip().lower()) for i in layer._APP_TYPES])
            )
        ]),
        choices=layer._APP_TYPES,
        type=str,
        required=True
    )
    _RUN_ARG_PARSER.add_argument(
        '-S',
        '--script',
        help="The relative or absolute path to a local Python script.",
        type=str,
        required=True
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

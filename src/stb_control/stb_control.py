#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#---------------------------
# Name: stb-control
#---------------------------

from importlib.metadata import version
from stb_control.logger import setup_logging, log

from pathlib import Path
import socket
import sys
import random

import argparse
from argparse import RawDescriptionHelpFormatter

from stb_control.stb_roku import RokuSTB
from stb_control.stb_android import AndroidSTB

class TrackOrderedPairs(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        # If no nargs is provided but the action behaves like
        # store_true, set nargs=0
        if kwargs.get('const') is True and kwargs.get('default') is False:
            nargs = 0
        super().__init__(option_strings, dest, nargs=nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        if not hasattr(namespace, 'command_sequence'):
            namespace.command_sequence = []

        # If values is a list (from nargs='+'), join it into a single string.
        # This normalizes both quoted and unquoted inputs!
        if isinstance(values, list):
            normalized_value = " ".join(values)
        else:
            normalized_value = values

        namespace.command_sequence.append((option_string, normalized_value))
        setattr(namespace, self.dest, normalized_value)


def process_command_line():
    '''All command line processing is done here.'''

    # appname = os.path.basename(sys.argv[0])

    parser = argparse.ArgumentParser(description='Open "deep links" on Roku and some Android devices.',
                                     formatter_class=RawDescriptionHelpFormatter,
                                     epilog='Default values are in ().\n')

    parser.add_argument('--debug', action='store_true',
                        help='turn on debug messages (%(default)s)')

    parser.add_argument('--quiet', action='store_true',
                        help='suppress progress messages (%(default)s)')

    parser.add_argument("--version", action="store_true",
                        help="Program version")

    parser.add_argument('--host', type=str, required=False,
                        default=socket.gethostname(),
                        metavar='<hostname>', help='backend hostname')

    parser.add_argument('--port', type=int, default=6544, metavar='<port>',
                        help='port number of the Services API (%(default)s)')

    parser.add_argument('--check-internet', action='store_true',
                        help='Check if internet is up')

    parser.add_argument('--sourceid', type=int, default=2, metavar='<Id>',
                        help='MythTV SourceId for callsign (%(default)s)')

    parser.add_argument('--device', type=str, required=True,
                        metavar='<device>', help='Android device'
                        '(e.g. onn1)')

    parser.add_argument('--wait', type=float, required=False,
                        action=TrackOrderedPairs,
                        metavar="<seconds (float)>",
                        help=('Wait this many seconds after sending '
                              'commands (%(default)s)'))

    parser.add_argument('--init', action='store_true',
                        help='Initialized the android device parameters')

    parser.add_argument('--reboot', action='store_true',
                        help='Reboot the android device')

    parser.add_argument('--apps', type=str, required=False,
                        metavar='<optional package name>')

    parser.add_argument('--state', action='store_true',
                        help='Get current state of device')

    parser.add_argument('--home', action=TrackOrderedPairs,
                        const=True, default=False)

    parser.add_argument('--reset', action='store_true',
                        help='Reset the android device')

    parser.add_argument('--test', action='store_true',
                        help='test a command')

    parser.add_argument('--getprompt', action='store_true',
                        help='Query device for any current prompt')

    parser.add_argument('--watchingprompt', action='store_true',
                        help='is the device asking "are you still watching"')

    parser.add_argument('--xmltvpath', type=Path, required=False,
                        default=Path("~mythtv/.xmltv").expanduser(),
                        metavar='<path>', help='xmltv file (%(default)s)')

    parser.add_argument('--configpath', type=Path, required=False,
                        default=Path("~mythtv/etc").expanduser(),
                        metavar='<path>', help='config file (%(default)s)')

    parser.add_argument('--prologue', type=str, required=False,
                        action=TrackOrderedPairs,
                        metavar="<service>",
                        help='Issue prologue "keys" for given service.')

    parser.add_argument('--epilogue', type=str, required=False,
                        action=TrackOrderedPairs,
                        metavar="<service>",
                        help='Issue epilogue "keys" for given service.')

    parser.add_argument('--link', type=str, required=False,
                        action=TrackOrderedPairs,
                        metavar="<str>",
                        help='Use a "deep" link to tune')

    parser.add_argument('--shell', type=str, required=False,
                        metavar="<str>",
                        help='Issue the "shell" command to adb')

    parser.add_argument('--recordid', type=int, default=0, metavar='<Id>',
                        help='MythTV RecordId (%(default)s)')

    parser.add_argument('--callsign', type=str,
                        metavar="<callsign>",
                        help='MythTV callsign to tune to')

    parser.add_argument('--description', type=str,
                        metavar="<show description>",
                        help='Description of show')

    parser.add_argument('--seriesid', type=str,
                        metavar="<seriesid>")

    parser.add_argument('--programid', type=str,
                        metavar="<programid>")

    parser.add_argument('--duration', type=int, metavar='<seconds>',
                        help='Show duration.')

    parser.add_argument('--touch', type=str,
                        metavar="<callsign>",
                        help='If channel has a bandwidth saver, '
                        '"touch" it to keep it from timing out')

    parser.add_argument('-k', '--keys',
                        action=TrackOrderedPairs, nargs='+',
                        help='Send keys to android device',
                        type=str, required=False)

    parser.add_argument('--message',
                        action=TrackOrderedPairs, nargs='+',
                        help='Log message',
                        type=str, required=False)

    parser.add_argument('--string', type=str, required=False,
                        action=TrackOrderedPairs,
                        help='Send a string to the android device')

    return parser.parse_args()


COMMAND_DISPATCH = {
    '--keys'     : "Keys",
    '--message'  : "Message",
    '--home'     : "Home",
    '--reboot'   : 'Reboot',
    '--link'     : "DeepLink",
    '--prologue' : "Prologue",
    '--epilogue' : "Epilogue",
    '--string'   : "SendString",
    '--state'    : "MediaState",
    '--wait'     : "Wait"
}


def check_internet():
    """
    Check if the internet is up by connecting to a stable server.
    """

    port = 53
    timeout = 2
    dnsservers = ['8.8.8.8', '4.4.4.4', '8.8.4.4', '1.1.1.1', '1.0.0.1',
                  '9.9.9.10', '149.112.112.10', '194.242.2.2',
                  '149.112.112.112', '1.0.0.2', '94.140.15.15']

    for idx in range(3):
        hostip = random.choice(dnsservers)

        try:
            # Create a socket (endpoint for network connection)
            # AF_INET means IPv4, SOCK_STREAM means TCP
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                s.connect((hostip, port))
                print(f"Internet ({hostip}) is up.", file=sys.stderr)
                return True
        except (socket.timeout, OSError):
            print(f"Internet ({hostip}) is down.", file=sys.stderr, flush=True)

    return False


def execute():
    args = process_command_line()

    __version__ = version("stb-control")

    if args.version:
        print(__version__)
        sys.exit(0)

    if not hasattr(args, 'command_sequence'):
        args.command_sequence = []

    if args.check_internet:
        return check_internet()

    which = args.device if args.device else 'Unknown'
    path = Path(f'{Path.home()}/log/{which}.log')

    try:
        setup_logging(path, args.debug, args.quiet)
    except Exception as e:
        print(f"Unable to setup log file: {e}")

    log.info(' '.join(sys.argv[1:]))

    device_name = args.device

    if device_name.startswith('roku'):
        device = RokuSTB(device_name)
    else:
        device = AndroidSTB(device_name)

    if device is None:
        log.error(f"Failed to open '{device_name}'")
        return False

    if args.reboot:
        return device.Reboot(device)
    if args.reset:
        return device.Reset(device)
    if args.shell:
        return device.Shell(device)
    if args.state:
        result = device.MediaState(device)
        log.info(result)
        return True

    # Process arg sequence
    for cmd, val in args.command_sequence:
        method_name = COMMAND_DISPATCH.get(cmd)
        if method_name:
            # Get the method from the device instance
            action_func = getattr(device, method_name, None)

            if action_func:
                # Call it and pass the required arguments
                if not action_func(val, args=args):
                    return False

    return True


def main():
    if not execute():
        sys.exit(1)
    sys.exit(0)

if __name__ == '__main__':
    main()

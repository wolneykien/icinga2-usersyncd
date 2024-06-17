# This file is a part of the icinga2_usersyncd Python package.
#
# Copyright (C) 2024  Paul Wolneykien <manowar@altlinux.org>
#
# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
# 02110-1301, USA.

"""
icinga2-usersyncd is a daemon to synchronize ApiUser entries with
Host agents on an Icinga 2 instance. This module implements the
command-line interface to the daemon and provides the entry-point
``main``.
"""

from .daemon import Daemon
from .logging import logger, logging
from .constants import VERSION_INFO, CONFIG, DEFAULT_QUEUE, DEFAULT_PREFIX, DEFAULT_TEMPLATES, DEFAULT_DELAY
import sys
import signal
from argparse import ArgumentParser
import os

def main() -> None:
    """
    The entry-point of the command-line interface to
    icinga2-usersyncd.
    """

    for s in signal.Signals:
        try:
            signal.signal(s, signal.SIG_IGN)
        except OSError:
            pass

    exit_on_signal = lambda s, f: sys.exit(0)
    signal.signal(signal.SIGTERM, exit_on_signal)
    signal.signal(signal.SIGQUIT, exit_on_signal)
    signal.signal(signal.SIGINT, exit_on_signal)

    parser = ArgumentParser(
        prog = VERSION_INFO['PROG'],
        description = '''
icinga2-usersyncd is a daemon to synchronize ApiUser entries with
Host agents on an Icinga 2 instance.
        '''.strip(),
        epilog = '''
For more information see icinga2-usersyncd(1).
Report bugs to https://bugzilla.altlinux.org/.
        '''.strip()
    )

    parser.add_argument(
        '-V', '--version',
        action = 'version',
        help = "show program's version information and exit",
        version = (f'''
%(PROG)s %(VERSION)s

Copyright (C) %(YEAR)s BaseALT Ltd.

License GPLv2+: GNU GPL version 2 or later <https://gnu.org/licenses/gpl.html>.

This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.

Written by Paul Wolneykien.
        ''' % VERSION_INFO).strip()
    )

    parser.add_argument('-v', '--verbose',
                        dest = 'log_level',
                        const = logging.DEBUG,
                        action = 'store_const',
                        help = 'show more messages')

    parser.add_argument('-q', '--quiet',
                        dest = 'log_level',
                        const = logging.ERROR,
                        action = 'store_const',
                        help = 'show less messages')

    parser.add_argument('-c', '--config', action = 'store',
                        dest = 'config',
                        default = CONFIG,
                        help = "configuration file "
                              f"(the default is %s)" % CONFIG)

    parser.add_argument('--no-config', action = 'store_const',
                        dest = 'config', const = None,
                        help = "do not use a configuration file")

    parser.add_argument('-L', '--url', dest = 'url', action = 'store',
                        help = 'Icinga 2 API URL')

    parser.add_argument('-u', '--username', action = 'store',
                        help = 'username to authenticate to Icinga 2 API')

    parser.add_argument('-p', '--password', action = 'store',
                        help = 'password to authenticate to Icinga 2 API')

    parser.add_argument('-C', '--cert', action = 'store',
                        help = 'certificate to authenticate to Icinga 2 API')

    parser.add_argument('-K', '--key', dest = 'key',
                        action = 'store',
                        help = 'key to authenticate to Icinga 2 API')

    parser.add_argument('-A', '--ca', dest = 'ca_cert',
                        action = 'store',
                        help = 'Icinga 2 API certificate (CA)')

    parser.add_argument('-Q', '--queue', action = 'store',
                        help = f"event queue name to use (the default is either from the config or '%s' if omitted)" % DEFAULT_QUEUE)

    parser.add_argument('-P', '--prefix', dest = 'prefix',
                        action = 'store',
                        help = f"a prefix for ApiUser names (the default is either from the config or '%s' if omitted)" % DEFAULT_PREFIX)

    parser.add_argument('-T', '--templates', action = 'store',
                        help = f"a set of templates each created ApiUser should import (the default is either from the config or [%s] if omitted)" % ", ".join(DEFAULT_TEMPLATES))

    parser.add_argument('-f', '--filter', action = 'store',
                        help = 'an optional Host filter string')

    parser.add_argument('-t', '--delay', dest = 'delay',
                        action = 'store',
                        help = f"a number of seconds to wait between connection attempts (the default is either from the config or %d if omitted)" % DEFAULT_DELAY)

    parser.add_argument('--setup',
                        dest = 'do_setup',
                        action = 'store_true',
                        help = 'generate certificate for CN "icinga2-usersyncd and exit')

    args = parser.parse_args()

    logger.setLevel(args.log_level or logging.INFO)

    if args.do_setup:
        os.system("/usr/sbin/icinga2 pki new-cert --cn icinga2-usersyncd --key /var/lib/icinga2/certs/icinga2-usersyncd.key --cert /var/lib/icinga2/certs/icinga2-usersyncd.crt")

    try:
        Daemon(config_file = args.config,
               url = args.url,
               username = args.username,
               password = args.password,
               certificate = args.cert,
               key = args.key,
               ca_certificate = args.ca_cert,
               queue = args.queue,
               prefix = args.prefix,
               templates = args.templates,
               filter = args.filter,
               delay = args.delay).run()
    except KeyboardInterrupt:
        pass

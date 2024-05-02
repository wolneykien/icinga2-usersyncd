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
from .constants import CONFIG
import sys
import signal

# TODO: CLI options for verbosity.
logger.setLevel(logging.DEBUG)

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

    try:
        Daemon(config_file = CONFIG).run()
    except KeyboardInterrupt:
        pass

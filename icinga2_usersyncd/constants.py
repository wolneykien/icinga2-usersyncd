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
Host agents on an Icinga 2 instance. This module defines a set of
constants used across the project.
"""

VERSION_INFO = {
    'PROG': "icinga2-usersyncd",
    'VERSION': "0.1.2",
    'YEAR': "2024"
}
CONFIG_SECTION = "daemon"
CONFIG = "/etc/sysconfig/icinga2-usersyncd"
DEFAULT_PREFIX = "host-"
DEFAULT_TEMPLATES = [ "usersync" ]
DEFAULT_QUEUE = "icinga2-usersyncd"
DEFAULT_DELAY = 1
SETUP_SCRIPT = "/usr/sbin/icinga2 pki new-cert --cn icinga2-usersyncd --key /var/lib/icinga2/certs/icinga2-usersyncd.key --csr /var/lib/icinga2/certs/icinga2-usersyncd.req && /usr/sbin/icinga2 pki sign-csr --csr /var/lib/icinga2/certs/icinga2-usersyncd.req --cert /var/lib/icinga2/certs/icinga2-usersyncd.crt"

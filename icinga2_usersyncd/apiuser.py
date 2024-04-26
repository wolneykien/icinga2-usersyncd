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
Host agents on an Icinga 2 instance. This module defines functions
to manage ApiUser objects on the Icinga 2.
"""

from typing import Sequence
from icinga2apic.client import Client # type: ignore
from .logging import logger
from .constants import DEFAULT_PREFIX, DEFAULT_TEMPLATES

class ApiUserManager():
    """
    Manages per-host ApiUser objects on an Icinga 2 inctance
    via REST API.
    """

    def __init__(self, client:Client, prefix: str = DEFAULT_PREFIX,
                 templates: Sequence[str] = DEFAULT_TEMPLATES):
        """
        Configures the manager to use the given client,
        given user name prefix and a set of user permissions.

        :param client: An Icinga 2 REST API client object.

        :param prefix: An optional user name prefix. The default
            prefix is "host-".

        :param templates: An set of custom templates the created
            ApiUser object should import. The  default value is
            "usersync".
        """

        self.client = client
        self.prefix = prefix
        self.templates = templates

    def add_api_user(self, hostname: str) -> None:
        """
        Sends request to Icinga 2 to add ApiUser for the
        host with the given name.

        :param hostname: The name of the host to add an ApiUser
            to create the ApiUser object for.
        """

        logger.debug(f"[ApiUser] Sending create request for API user '%s' for host '%s'..." % ((self.prefix + hostname), hostname))

        resp = self.client.objects.create(
            "ApiUser", self.prefix + hostname,
            templates = self.templates,
            attrs = {
                "client_cn": hostname
            }
        )

    def del_api_user(self, hostname: str) -> None:
        """
        Sends request to Icinga 2 to delete ApiUser for host
        with the given name.

        :param client: An Icinga 2 client object.

        :param hostname: The name of the host to delete the ApiUser
            object for.
        """

        logger.debug(f"[ApiUser] Sending delete request for API user '%s'..." % (self.prefix + hostname))

        resp = self.client.objects.delete(
            "ApiUser", self.prefix + hostname
        )

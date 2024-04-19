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
Host agents on an Icinga 2 instance. This module defines a
Comparator that synchronizes ApiUser records with all Host objects,
that are configured on the Icinga 2 server.
"""

from typing import Optional, Generator
from icinga2apic.client import Client # type: ignore
from .logging import logger
from .apiuser import add_api_user, del_api_user

class Comparator():
    """
    The Comparator requests configured Hosts and ApiUser
    objects and synchronize them by creating new ApiUser objects
    when there's no one for an existing Host, and deleting existing
    ones that have no corresponding Host objects.
    """

    def __init__(self,
                 client: Client,
                 filter: Optional[str] = None):
        """
        :param filter: An optional Host filter string (i. e.
            ``host.zone == "master"``). If specified, overrides the
            value specified in the configuration file under the
            ``[daemon]`` section.
        """

        self.client = client
        self.filter = filter

    def run(self) -> None:
        """
        Runs the user synchronization proc by comparing Host and
        ApiUser lists.
        """

        logger.debug("[Comparator] Requesting list of Hosts...")
        hosts = self.client.objects.list("Host", filters = self.filter)

        logger.debug("[Comparator] Requesting list of ApiUsers...")
        apiusers = self.client.objects.list("ApiUser")

        u_names = set([u["name"] for u in apiusers])
        h_names = set([h["name"] for u in hosts])

        for name in (h_names - u_names):
            try:
                add_api_user(client, name)
            except Exception as ex:
                logger.error(f"[Comparator] Error while trying to add ApiUser \"%s\": %s." % (name, str(ex)))

        for name in (u_names - h_names):
            try:
                del_api_user(client, name)
            except Exception as ex:
                logger.error(f"[Comparator] Error while trying to add ApiUser \"%s\": %s." % (name, str(ex)))

        logger.info("[Comparator] ApiUsers synchronized.")


# client.objects.list('Host',
#                     filters='host.zone == zone',
#                     filter_vars={'zone': zone})
#
# types = ['ObjectCreated', 'ObjectDeleted']
# queue = queue
# filter = 'event.object_type == "Host"'
#
# for event in client.events.subscribe(types, queue, filter):
#     print(event)
#
#{"object_name":"test1","object_type":"Host","timestamp":1711707986.404245,"type":"ObjectCreated"}

## curl -k -sS -i -u 'root:bcf6ca38a4d66d17' -H 'Accept: application/json' -X POST 'https://localhost:5665/v1/events' -d '{ "queue": "abc", "types": ["ObjectCreated", "ObjectDeleted"], "filter": "event.object_type == \"Host\"" }'

#{"object_name":"test4","object_type":"Host","timestamp":1711708483.735119,"type":"ObjectCreated"}

#{"object_name":"test4","object_type":"Host","timestamp":1711708571.37147,"type":"ObjectDeleted"}

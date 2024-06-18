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
Host agents on an Icinga 2 instance. This module defines an
EventListener that watchs for Host object creation and removal
events and translates them into corresponding ApiUser add and
remove calls.
"""

from typing import Optional, Generator
from icinga2apic.client import Client # type: ignore
from threading import Lock
from .logging import logger
from .apiuser import ApiUserManager
from .constants import DEFAULT_QUEUE
import json

class EventListener():
    """
    The EventListener is able to watch for Host object creation
    and removal events and translate them into corresponding
    ApiUser add and remove calls.
    """

    def __init__(self,
                 client: Client,
                 userManager: ApiUserManager,
                 queue: Optional[str] = None,
                 filter: Optional[str] = None):
        """
        :param client: An Icinga 2 REST API client object.

        :param userManager: An ApiUserManager instance.

        :param queue: A queue name value to be used with
            the Icinga 2 event API. The default value is
            ``icinga2-usersyncd``.

        :param filter: An optional Host filter string (i. e.
            ``host.zone == "master"``).
        """

        self.client = client
        self.queue = queue or DEFAULT_QUEUE
        self.filter = filter
        self.stream: Optional[Generator] = None
        self.lock = Lock()
        self.userManager = userManager

    def connect(self) -> None:
        """
        Opens the request to the event stream.
        """

        logger.debug("[EventListener] Requesting inistal host list...")
        hosts = self.client.objects.list("Host", filters = self.filter)
        self.host_names = set([h["name"] for h in hosts])

        def subscribe() -> Generator:
            return self.client.events.subscribe(
                ['ObjectCreated', 'ObjectDeleted'],
                self.queue,
                "event.object_type == \"Host\""
            )

        with self.lock:
            if self.stream:
                raise RuntimeError("Already run!")
            logger.debug("[EventListener] Requesting host create and delete events...")
            self.stream = subscribe()

    def run(self) -> None:
        """
        Runs the user synchronization proc for each created host.
        """

        with self.lock:
            if not self.stream:
                raise RuntimeError("Not connected!")
            try:
                for str_e in self.stream:
                    e = json.loads(str_e)
                    if e["object_type"] != "Host":
                        continue
                    if e["type"] == "ObjectCreated":
                        try:
                            host = self.client.objects.list(
                                "Host",
                                filters = (f"host.name == \"%s\"" % e["object_name"]) + (f" && (%s)" % self.filter) if self.filter else ""
                            )[0]
                            if host:
                                self.host_names.add(host["name"])
                                self.userManager.add_api_user(host["name"])
                        except Exception as ex:
                            logger.error(f"[EventListener] Error while trying to add ApiUser \"%s\": %s." % (e["object_name"], str(ex)))
                    elif e["type"] == "ObjectDeleted":
                        try:
                            if e["object_name"] in self.host_names:
                                self.host_names.remove(e["object_name"])
                                self.userManager.del_api_user(
                                    e["object_name"]
                                )
                        except Exception as ex:
                            logger.error(f"[EventListener] Error while trying to delete ApiUser \"%s\": %s." % (e["object_name"], str(ex)))
            except Exception as ex:
                logger.error(f"[EventListener] Error while processing the stream: %s." % str(ex))
            finally:
                self.stream.close()
                logger.info("[EventListener] Connection closed.")

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

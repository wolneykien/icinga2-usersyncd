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
Host agents on an Icinga 2 instance. This module defines the main
class that encapsulates all functions.
"""

from typing import Optional
from icinga2apic.client import Client # type: ignore
from .event_listener import EventListener
from .comparator import Comparator
from .logging import logger
from .apiuser import ApiUserManager
from multiprocessing import Process
import time

# from importlib.resources import files
#

class Daemon:
    """
    Represents the icinga2-usersyncd daemon.
    """

    def __init__(self,
                 config_file: Optional[str] = None,
                 url: Optional[str] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 certificate: Optional[str] = None,
                 key: Optional[str] = None,
                 ca_certificate: Optional[str] = None):
        """
        :param config_file: A path to configuration file, usually
            ``/etc/sysconfig/icinga2-usersyncd`` with ``[api]`` and
            ``[daemon]`` sections, which define connection parameters
            for ``icinga2apic.client`` and an optional filter for Host
            objects.

        :param url: The Icinga 2 API URL to connect to. If specified,
            overrides the value specified in the configuration file
            under the ``[api]`` section.

        :param username: An optional username for BASIC authentication
            on the Icinga 2 API. If specified, overrides the value
            specified in the configuration file under the ``[api]``
            section.

        :param username: An optional password for BASIC authentication
            on the Icinga 2 API. If specified, overrides the value
            specified in the configuration file under the ``[api]``
            section.

        :param certificate: An optional path to the user certificate
            for authentication on the Icinga 2 API. If specified,
            overrides the value specified in the configuration file
            under the ``[api]`` section.

        :param key: A path to the private key for user certificate.
            Required if certificate is not None. If specified,
            overrides the value specified in the configuration file
            under the ``[api]`` section.

        :param ca_certificate: The Icinga 2 CA certificate used to
            verify the API connection. If specified, overrides the
            value specified in the configuration file under the
            ``[api]`` section.
        """

        logger.debug("Initializing the Icinga 2 API client...")
        self.client = Client(
            config_file = config_file,
            url = url,
            username = username,
            password = password,
            certificate = certificate,
            key = certificate,
            ca_certificate = ca_certificate
        )

        self.userManager = ApiUserManager(self.client)

    def run(self) -> None:
        """
        Runs the icinga2-usersyncd daemon.
        """

        logger.info("Trying to connect the listener...")

        while True:
            listener = EventListener(self.client, self.userManager)

            try:
                listener.connect()
            except:
                logger.debug("Listener not connected. Making a retry after a timeout...")
                time.sleep(1)
                continue

            logger.info("Listener connected.")

            listener_p = Process(
                target = listener.run,
                name = "EventListener",
                daemon = True
            )
            listener_p.start()

            comparator_p = Process(
                target = self.comparator_loop,
                name = "ComparatorLoop",
                daemon = True
            )
            comparator_p.start()

            listener_p.join()
            logger.info("Listener finished. Making a retry after a timeout...")

            comparator_p.terminate()
            comparator_p.join()

            time.sleep(1)

    def comparator_loop(self) -> None:
        """
        Runs the Comparator. Makes a restart on error.
        """

        while True:
            comparator = Comparator(self.client, self.userManager)
            try:
                comparator.run()
                break
            except:
                logger.debug("Comparator exited with an error. Making a retry after a timeout...")
                time.sleep(1)

        logger.info("Comparator finished.")

# from icinga2apic.client import Client
#
# client = Client(config_file='/etc/sysconfig/icinga2-apiusers-sync')
#
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
#{"object_name":"test3","object_type":"Host","timestamp":1711708583.605244,"type":"ObjectDeleted"}
#{"object_name":"test2","object_type":"Host","timestamp":1711708588.958552,"type":"ObjectDeleted"}
#{"object_name":"test1","object_type":"Host","timestamp":1711708592.050786,"type":"ObjectDeleted"}

#object ApiUser h {
#    client_cn = h
#    permissions = [{
#      permission = "actions/process-check-result"
#      filter = {{ host.name == h }}
#    }]
#  }

#actions/remove-acknowledgement

#icinga2 pki new-cert --cn icinga2-usersyncd --csr /tmp/icinga2-usersyncd.csr --key /tmp/icinga2-usersyncd.key --cert /tmp/icinga2-usersyncd.crt
#icinga2 pki sign-csr --cert /tmp/icinga2-usersyncd.crt --csr /tmp/icinga2-usersyncd.csr

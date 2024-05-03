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

from typing import Optional, Sequence
from icinga2apic.client import Client # type: ignore
from .event_listener import EventListener
from .comparator import Comparator
from .logging import logger
from .apiuser import ApiUserManager
from .constants import CONFIG_SECTION, DEFAULT_DELAY
from multiprocessing import Process
import time
from configparser import ConfigParser, NoOptionError

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
                 ca_certificate: Optional[str] = None,
                 queue: Optional[str] = None,
                 prefix: Optional[str] = None,
                 templates: Optional[Sequence[str]] = None,
                 filter: Optional[str] = None,
                 delay: Optional[float] = None):
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

        :param ca_certificate: The Icinga 2 CA certificate to be
            used to verify the API connection. If specified, overrides
            the value specified in the configuration file under the
            ``[api]`` section.

        :param queue: A queue name to be used with the Icinga 2
            event API. The default value is
            ``icinga2-usersyncd``. If specified, overrides the
            value specified in the configuration file under the
            ``[daemon]`` section.

        :param prefix: A user name prefix. The default
            prefix is "host-". If specified, overrides the
            value specified in the configuration file under the
            ``[daemon]`` section.

        :param templates: A set of custom templates the created
            ApiUser object should import. The  default value is
            "usersync". If specified, overrides the
            value specified in the configuration file under the
            ``[daemon]`` section.

        :param filter: An optional Host filter string (i. e.
            ``host.zone == "master"``). If specified, overrides the
            value specified in the configuration file under the
            ``[daemon]`` section.

        :param dealy: A number of seconds to wait between connection
            attempts. The default is 1 second. If specified, overrides
            the value specified in the configuration file under the
            ``[daemon]`` section.
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

        logger.debug("Initializing the daemon...")
        if config_file:
            config = ConfigParser()
            config.read(config_file)

            if config.has_section(CONFIG_SECTION):
                self.queue = queue or config.get(
                    CONFIG_SECTION, "queue",
                    fallback = None
                ) or None
                self.prefix = prefix or config.get(
                    CONFIG_SECTION, "prefix",
                    fallback = None
                ) or None
                self.templates = templates or [
                    t.strip() for t in config.get(
                        CONFIG_SECTION, "templates",
                        fallback = ""
                    ).split(",") if t
                ] or None
                self.filter = filter or config.get(
                    CONFIG_SECTION, "filter",
                    fallback = None
                ) or None
                self.delay = delay or float(config.get(
                    CONFIG_SECTION, "delay",
                    fallback = DEFAULT_DELAY
                ))

        self.userManager = ApiUserManager(self.client,
                                          prefix = self.prefix,
                                          templates = self.templates)

    def run(self) -> None:
        """
        Runs the icinga2-usersyncd daemon.
        """

        logger.info("Trying to connect the listener...")

        while True:
            listener = EventListener(self.client,
                                     self.userManager,
                                     queue = self.queue,
                                     filter = self.filter)

            try:
                listener.connect()
            except Exception as ex:
                logger.error(f"Listener not connected: %s. Making a retry after a timeout..." % str(ex))
                time.sleep(self.delay)
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

            time.sleep(self.delay)

    def comparator_loop(self) -> None:
        """
        Runs the Comparator. Makes a restart on error.
        """

        while True:
            comparator = Comparator(self.client,
                                    self.userManager,
                                    filter = self.filter)
            try:
                comparator.run()
                break
            except Exception as ex:
                logger.error(f"Comparator exited with an error: %s. Making a retry after a timeout..." % str(ex))
                time.sleep(self.delay)

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

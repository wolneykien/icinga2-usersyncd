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

from icinga2apic.client import Client # type: ignore
from .logging import logger

def add_api_user(client: Client, name: str) -> None:
    """
    Sends request to Icinga 2 to add ApiUser with the
    given name.

    :param client: An Icinga 2 client object.

    :param name: The name of the ApiUser to create.
    """

    resp = client.objects.create("ApiUser", name, None, {
    })

def del_api_user(client: Client, name: str) -> None:
    """
    Sends request to Icinga 2 to delete ApiUser with the
    given name.

    :param client: An Icinga 2 client object.

    :param name: The name of the ApiUser to delete.
    """

    resp = client.objects.delete("ApiUser", name)

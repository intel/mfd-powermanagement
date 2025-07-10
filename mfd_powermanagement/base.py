# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Module for base."""

import logging
import typing
from abc import ABC, abstractmethod
from ipaddress import ip_address

from mfd_connect import LocalConnection
from mfd_common_libs import add_logging_level, log_levels

if typing.TYPE_CHECKING:
    from mfd_connect import Connection

logger = logging.getLogger(__name__)
add_logging_level("MODULE_DEBUG", log_levels.MODULE_DEBUG)


class PowerManagement(ABC):
    """Abstraction of managing power on machine."""

    def __init__(
        self,
        host: str = None,
        ip: str = None,
        username: str = None,
        password: str = None,
        executable_name: str = None,
        *,
        connection: "Connection" = LocalConnection(),
    ):
        """
        Init of PowerManagement.

        :param connection: Not required if you need local execution, for remote execution required Connection object
        from mfd_connect
        :param executable_name: Name of application for controlling management device
        :param ip: IP address of target device. Not required if `host` is provided.
        :param host: Hostname of target device. Not required if `ip` is provided.
        :param password: Password of target device
        :param username: user to authentication
        :param connection: Not required if you need local execution, for remote execution required Connection object
        from mfd_connect
        """
        self._connection = connection

        if host:
            self._host = host.strip()
        elif ip:
            self._host = ip_address(ip.strip())
        if not ip and not host:
            raise ValueError("Either ip or host must be set")

        self._username = username
        self._password = password
        self._executable_name = executable_name

    @abstractmethod
    def set_state(self, **kwargs) -> bool:
        """Set given power state."""
        pass

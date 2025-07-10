# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Module for SystemPowerManagement powermanagement."""

from abc import abstractmethod
from typing import TYPE_CHECKING, List

from mfd_typing import OSName

from ..base import PowerManagement
from ..exceptions import OSNotSupported

if TYPE_CHECKING:
    from mfd_connect import Connection

    from ..data_structures import SystemPowerState


class SystemPowerManagement(PowerManagement):
    """Base class of system based power management."""

    def __new__(cls, connection: "Connection", *args, **kwargs):
        """
        Choose SystemPowerManagement subclass based on provided connection object.

        :param connection: Connection
        :return: Instance of SystemPowerManagement subclass
        """
        if cls != SystemPowerManagement:
            return super().__new__(cls, *args, **kwargs)

        from .linux import LinuxPowerManagement
        from .windows import WindowsPowerManagement
        from .freebsd import FreeBSDPowerManagement

        os_name = connection.get_os_name()
        os_name_to_class = {
            OSName.WINDOWS: WindowsPowerManagement,
            OSName.LINUX: LinuxPowerManagement,
            OSName.FREEBSD: FreeBSDPowerManagement,
        }

        owner_class = os_name_to_class.get(os_name)
        if owner_class is None:
            raise OSNotSupported(f"Not supported OS for {cls.__name__}: {os_name}")

        return super().__new__(owner_class, *args, **kwargs)

    def __init__(self, *, connection: "Connection"):
        """
        Init.

        Not calling super().__init__ here, because we don't want it's params and logic to be called.
        But we want to inherit from PowerManagement to provide common API.

        :param connection: Connection
        """
        self._connection = connection

    @abstractmethod
    def get_available_power_states(self) -> List["SystemPowerState"]:
        """
        Get available power states.

        :return: List of available states
        """

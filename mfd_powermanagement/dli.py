# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Module for controlling Digital Loggers web power switches."""

import dlipower
from enum import Enum
from .base import PowerManagement
from mfd_common_libs import os_supported
from mfd_typing import OSName
from mfd_connect import LocalConnection


class DliSocketPowerStates(Enum):
    """Available states in PowerManagement."""

    on = "on"
    off = "off"


class DLI(PowerManagement):
    """
    Implementation of Digital Loggers web power switches management.

    Usage example (for derived class):
    >>> power_switch = DLI(connection=LocalConnection(), ip='10.10.10.10', user='admin' password='*****')
    >>> power_switch.power_on(outlet_number=5)
    Outlet no. 5 is powered on
    >>>
    >>> power_switch.power_cycle(outlet_number=2, time_delay=15)
    Outlet no. 2 is power cycled.
    """

    @os_supported(OSName.WINDOWS, OSName.LINUX, OSName.ESXI, OSName.FREEBSD)
    def __init__(
        self,
        host: str = None,
        ip: str = None,
        username: str = None,
        password: str = None,
        *,
        connection: LocalConnection = LocalConnection(),
    ):
        """
        Init of Digital Logic web power switch.

        :param host: Hostname of target device. Not required if `ip` is provided.
        :param password: Password of target device
        :param username: user to authentication
        :param ip: **NOT USED, declared only to match base class params**
        :param connection: Not required if you need local execution, for remote execution required Connection object
        from mfd_connect
        """
        PowerManagement.__init__(
            self,
            connection=connection,
            host=host,
            ip=ip,
            username=username,
            password=password,
            executable_name=None,
        )

        self.wps = dlipower.PowerSwitch(hostname=self._host, userid=self._username, password=self._password)

    def power_off(self, *, outlet_number: int) -> bool:
        """
        Power off the specified outlet.

        :param outlet_number: Number of electrical socket to be controlled.
        :returns True (operation succeeded) or false (operation failed).
        """
        return self.wps.off(outlet=outlet_number)

    def power_on(self, *, outlet_number: int) -> bool:
        """
        Power on the specified outlet.

        :param outlet_number: Number of electrical socket to be controlled.
        :returns True (operation succeeded) or false (operation failed).
        """
        return self.wps.on(outlet=outlet_number)

    def power_cycle(self, *, outlet_number: int, time_delay: int) -> bool:
        """
        Power cycle the specified outlet. The cycle delay depends on the PDU setting for the outlet.

        :param outlet_number: Number of electrical socket to be controlled.
        :param time_delay: Power cycle time delay in seconds.
        :returns True (operation succeeded) or false (operation failed).
        """
        self.wps.cycletime = time_delay
        return self.wps.cycle(outlet=outlet_number)

    def set_state(self, *, state: DliSocketPowerStates, outlet_number: int) -> bool:
        """Set given power state for a particular socket."""
        if state.value == "on":
            return self.power_on(outlet_number=outlet_number)
        else:
            return self.power_off(outlet_number=outlet_number)

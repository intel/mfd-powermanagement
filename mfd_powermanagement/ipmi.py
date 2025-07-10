# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Module for IPMI."""

import logging
import time
import typing
from enum import Enum

from .base import PowerManagement
from .exceptions import PowerManagementException
from mfd_common_libs import add_logging_level, log_levels, os_supported
from mfd_connect import LocalConnection
from mfd_typing import OSName

if typing.TYPE_CHECKING:
    from mfd_connect import Connection

logger = logging.getLogger(__name__)
add_logging_level("MODULE_DEBUG", log_levels.MODULE_DEBUG)


class IpmiType(Enum):
    """Available IPMI tools and corresponding version check."""

    IPMITool = "ipmitool"
    IPMIUtil = "ipmiutil"


ipmi_ver = {IpmiType.IPMIUtil: "ipmiutil ver", IpmiType.IPMITool: "ipmitool -V"}


class IpmiStates(Enum):
    """Available states in PowerManagement."""

    up = {IpmiType.IPMIUtil.value: "-u", IpmiType.IPMITool.value: "on"}
    down = {IpmiType.IPMIUtil.value: "-d", IpmiType.IPMITool.value: "off"}
    reset = {IpmiType.IPMIUtil.value: "-r", IpmiType.IPMITool.value: "reset"}
    cycle = {IpmiType.IPMIUtil.value: "-c", IpmiType.IPMITool.value: "cycle"}
    soft = {IpmiType.IPMIUtil.value: "-D", IpmiType.IPMITool.value: "soft"}


class Ipmi(PowerManagement):
    """
    Implementation of managing power on machine by IPMITool or IpmiUtil.

    Usage example:
    >>> powermanagement = Ipmi(ip="10.10.10.10",username='admin',password='*****')
    >>> powermanagement.powercycle()
    Machine is rebooting
    >>>
    >>> powermanagement.set_state(state=IpmiStates.down)
    Machine is poweroff by AC
    """

    @os_supported(OSName.WINDOWS, OSName.LINUX, OSName.ESXI, OSName.FREEBSD)
    def __init__(
        self,
        host: str = None,
        ip: str = None,
        username: str = None,
        password: str = None,
        ipmi_type: IpmiType = IpmiType.IPMIUtil,
        *,
        connection: "Connection" = LocalConnection(),
    ):
        """
        Init of IPMI.

        :param ip: IP address of target device. Not required if `host` is provided.
        :param host: Hostname of target device. Not required if `ip` is provided.
        :param password: Password of target device
        :param username: user to authentication
        :param ipmi_type: Choose between available tools.
        :param connection: Not required if you need local execution, for remote execution required Connection object
        from mfd_connect
        """
        super().__init__(host, ip, username, password, ipmi_type.value, connection=connection)

        tool_availability_test_command = ipmi_ver[ipmi_type]
        try:
            result = self._connection.execute_command(
                tool_availability_test_command, shell=False, expected_return_codes={0, 127, 234}
            ).stderr
            if "command not found" in result:
                raise FileNotFoundError
        except FileNotFoundError:
            raise PowerManagementException(f"{self._executable_name} is not available in OS")

    def powercycle(self) -> None:
        """Reset platform by setting down and up state with delay."""
        logger.log(level=log_levels.MODULE_DEBUG, msg="Resetting platform via IPMI and looking for reboot prompts...")
        self.set_state(state=IpmiStates.down, retry_count=3)
        time.sleep(10)
        self.set_state(state=IpmiStates.up, retry_count=3)

    def power_down(self) -> None:
        """Power off platform."""
        self.set_state(state=IpmiStates.down, retry_count=3)

    def power_up(self) -> None:
        """Power on platform."""
        self.set_state(state=IpmiStates.up, retry_count=3)

    def _set_state_command(self, state: IpmiStates) -> str:
        """
        Create command based on the tool used.

        :param state: State to set.
        """
        if self._executable_name == IpmiType.IPMIUtil.value:
            return (
                f"{self._executable_name} power -F lan2 -N {self._host} "
                f"-U {self._username} -P {self._password} {state.value[self._executable_name]} -V 4"
            )
        if self._executable_name == IpmiType.IPMITool.value:
            return (
                f"{self._executable_name} -I lanplus -H {self._host} "
                f"-U {self._username} -P {self._password} chassis power {state.value[self._executable_name]}"
            )

    def set_state(self, *, state: IpmiStates, retry_count: int = 3) -> None:
        """
        Set given power state. Cannot set state, which is already set.

        :param state: State to set
        :param retry_count: Number of times to retry on failure
        """
        if retry_count == 0:
            logger.log(level=log_levels.MODULE_DEBUG, msg="Multiple (on failure) IPMI calls attempt timed out")
            raise PowerManagementException(
                f"Multiple failure on calls, cannot set {state.value[self._executable_name]}"
            )

        command = self._set_state_command(state)

        process = self._connection.execute_command(command)
        output = process.stdout

        if "completed successfully" not in output and "chassis power" not in output.casefold():
            logger.log(level=log_levels.MODULE_DEBUG, msg=f"set_state output: {output}")
            logger.log(
                level=log_levels.MODULE_DEBUG,
                msg=f"Unable to perform action: {state.name} - Attempts left: {retry_count}",
            )
            self.set_state(state=state, retry_count=retry_count - 1)
        else:
            logger.log(level=log_levels.MODULE_DEBUG, msg=f"set_state output: {output}")
            logger.log(
                level=log_levels.MODULE_DEBUG,
                msg=f"Action performed successfully: Chassis {state.value[self._executable_name]}",
            )

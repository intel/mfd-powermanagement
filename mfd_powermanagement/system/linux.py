# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Module for LinuxPowerManagement powermanagement."""

from typing import List

from .base import SystemPowerManagement
from ..data_structures import SystemPowerState
from ..exceptions import PowerManagementException


class LinuxPowerManagement(SystemPowerManagement):
    """Linux based power management."""

    def set_state(self, state: SystemPowerState) -> None:
        """
        Set given power state.

        :param state: SystemPowerState field
        """
        available_states = self.get_available_power_states()
        if state not in available_states:
            raise PowerManagementException(f"System is not supporting state: {state}")

        if state is SystemPowerState.S5:
            self._connection.shutdown_platform()
            return

        if state is SystemPowerState.S3:
            self._connection.execute_command("echo deep > /sys/power/mem_sleep", shell=True)

        self._connection.execute_command(f"echo {state.value} > /sys/power/state", shell=True)

    def get_available_power_states(self) -> List[SystemPowerState]:
        """
        Get available power states.

        :return: List of available states
        """
        output = self._connection.execute_command("cat /sys/power/state").stdout

        known_states = [state.value for state in SystemPowerState]
        available_states = [SystemPowerState(state) for state in output.split() if state in known_states]
        if SystemPowerState.S5 not in available_states:
            available_states.append(SystemPowerState.S5)

        return available_states

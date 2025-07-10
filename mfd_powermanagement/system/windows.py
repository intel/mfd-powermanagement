# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Module for WindowsPowerManagement powermanagement."""

from typing import List

from .base import SystemPowerManagement
from ..data_structures import SystemPowerState
from ..exceptions import PowerManagementException


class WindowsPowerManagement(SystemPowerManagement):
    """Windows based power management."""

    def set_state(self, state: SystemPowerState) -> None:
        """
        Set given power state.

        :param state: SystemPowerState field
        """
        if state is SystemPowerState.S5:
            self._connection.shutdown_platform()
            return

        if state is SystemPowerState.S3:
            command = "powercfg /hibernate off & rundll32.exe powrprof.dll,SetSuspendState Sleep"
        elif state is SystemPowerState.S4:
            command = "powercfg /hibernate on & rundll32.exe powrprof.dll,SetSuspendState 0,1,0"
        else:
            raise PowerManagementException(f"State {state} is not supported.")

        self._connection.execute_command(command)

    def get_available_power_states(self) -> List[SystemPowerState]:
        """
        Get available power states.

        :return: List of available states
        """
        raise NotImplementedError

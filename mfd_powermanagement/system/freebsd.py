# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Module for FreeBSDPowerManagement powermanagement."""

from typing import List

from .base import SystemPowerManagement
from ..data_structures import SystemPowerState
from ..exceptions import PowerManagementException


class FreeBSDPowerManagement(SystemPowerManagement):
    """FreeBSD based power management."""

    def set_state(self, state: SystemPowerState) -> None:
        """
        Set given power state.

        :param state: SystemPowerState field
        """
        available_states = self.get_available_power_states()
        if state not in available_states:
            raise PowerManagementException(f"System does not support state: {state}")

        self._connection.execute_command(f"acpiconf -s {state.name}")

    def get_available_power_states(self) -> List[SystemPowerState]:
        """
        Get available power states.

        :return: List of available states
        """
        output = self._connection.execute_command("sysctl -n hw.acpi.supported_sleep_state").stdout

        available_states = [
            getattr(SystemPowerState, state) for state in output.split() if hasattr(SystemPowerState, state)
        ]
        if SystemPowerState.S5 not in available_states:
            available_states.append(SystemPowerState.S5)

        return available_states

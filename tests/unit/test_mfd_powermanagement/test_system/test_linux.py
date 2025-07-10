# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT

from unittest.mock import call

import pytest
from mfd_connect import RPyCConnection
from mfd_connect.base import ConnectionCompletedProcess
from mfd_typing import OSName

from mfd_powermanagement.data_structures import SystemPowerState
from mfd_powermanagement.exceptions import PowerManagementException
from mfd_powermanagement.system.linux import LinuxPowerManagement


class TestLinuxPowerManagement:
    @pytest.fixture()
    def system_pm(self, mocker):
        conn = mocker.create_autospec(RPyCConnection)
        conn.get_os_name.return_value = OSName.LINUX
        yield LinuxPowerManagement(connection=conn)
        mocker.stopall()

    def test_set_state(self, mocker, system_pm):
        system_pm.get_available_power_states = mocker.Mock(
            return_value=[SystemPowerState.S3, SystemPowerState.S4, SystemPowerState.S5]
        )

        system_pm.set_state(SystemPowerState.S5)
        system_pm._connection.shutdown_platform.assert_called_once()

        system_pm.set_state(SystemPowerState.S4)
        system_pm._connection.execute_command.assert_called_once_with("echo disk > /sys/power/state", shell=True)

        system_pm._connection.execute_command.reset_mock()
        system_pm.set_state(SystemPowerState.S3)
        system_pm._connection.execute_command.assert_has_calls(
            [
                call("echo deep > /sys/power/mem_sleep", shell=True),
                call("echo mem > /sys/power/state", shell=True),
            ]
        )

        with pytest.raises(PowerManagementException):
            system_pm.set_state(SystemPowerState.S1)

    def test_get_available_power_states(self, system_pm):
        system_pm._connection.execute_command.return_value = ConnectionCompletedProcess(
            args="", stdout="mem disk", stderr=""
        )
        assert system_pm.get_available_power_states() == [
            SystemPowerState.S3,
            SystemPowerState.S4,
            SystemPowerState.S5,
        ]

# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT

import pytest
from mfd_connect import RPyCConnection
from mfd_typing import OSName

from mfd_powermanagement.data_structures import SystemPowerState
from mfd_powermanagement.exceptions import PowerManagementException
from mfd_powermanagement.system.windows import WindowsPowerManagement


class TestWindowsPowerManagement:
    @pytest.fixture()
    def system_pm(self, mocker):
        conn = mocker.create_autospec(RPyCConnection)
        conn.get_os_name.return_value = OSName.WINDOWS
        yield WindowsPowerManagement(connection=conn)

    def test_set_state(self, system_pm):
        system_pm.set_state(SystemPowerState.S5)
        system_pm._connection.shutdown_platform.assert_called_once()

        system_pm.set_state(SystemPowerState.S3)
        system_pm._connection.execute_command.assert_called_once_with(
            "powercfg /hibernate off & rundll32.exe powrprof.dll,SetSuspendState Sleep"
        )

        system_pm._connection.execute_command.reset_mock()
        system_pm.set_state(SystemPowerState.S4)
        system_pm._connection.execute_command.assert_called_once_with(
            "powercfg /hibernate on & rundll32.exe powrprof.dll,SetSuspendState 0,1,0"
        )

        with pytest.raises(PowerManagementException):
            system_pm.set_state(SystemPowerState.S1)

# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT

import pytest
from mfd_connect import RPyCConnection
from mfd_connect.base import ConnectionCompletedProcess
from mfd_typing import OSName

from mfd_powermanagement.data_structures import SystemPowerState
from mfd_powermanagement.exceptions import PowerManagementException
from mfd_powermanagement.system.freebsd import FreeBSDPowerManagement


class TestFreeBSDPowerManagement:
    @pytest.fixture()
    def system_pm(self, mocker):
        conn = mocker.create_autospec(RPyCConnection)
        conn.get_os_name.return_value = OSName.FREEBSD
        yield FreeBSDPowerManagement(connection=conn)

    def test_set_state(self, mocker, system_pm):
        system_pm.get_available_power_states = mocker.Mock(return_value=[SystemPowerState.S4, SystemPowerState.S5])

        system_pm.set_state(SystemPowerState.S4)
        system_pm._connection.execute_command.assert_called_once_with("acpiconf -s S4")

        with pytest.raises(PowerManagementException):
            system_pm.set_state(SystemPowerState.S1)

    def test_get_available_power_states(self, system_pm):
        system_pm._connection.execute_command.return_value = ConnectionCompletedProcess(
            args="", stdout="S4 S5", stderr=""
        )
        assert system_pm.get_available_power_states() == [SystemPowerState.S4, SystemPowerState.S5]

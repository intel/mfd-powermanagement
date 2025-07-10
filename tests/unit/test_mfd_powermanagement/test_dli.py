# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
import pytest
import mfd_powermanagement.base
from mfd_powermanagement import DLI, DliSocketPowerStates
from mfd_connect import Connection
from mfd_typing import OSName


@pytest.fixture()
def prepare_connection_mocks(mocker):
    mocker.patch("dlipower.PowerSwitch", autospec=True)
    mocker.patch.object(mfd_powermanagement.base.PowerManagement, "_host", "127.0.0.1", create=True)
    mocker.patch.object(mfd_powermanagement.base.PowerManagement, "_username", create=True)
    mocker.patch.object(mfd_powermanagement.base.PowerManagement, "_password", create=True)

    conn = mocker.create_autospec(Connection)
    conn.get_os_name.return_value = OSName.LINUX

    return conn


class TestDLI:
    def test_power_on(self, mocker, prepare_connection_mocks):
        dli = DLI(connection=prepare_connection_mocks, ip="127.0.0.1", username="admin", password="........")
        mocker.patch.object(dli.wps, "on")

        dli.power_on(outlet_number=1)

        dli.wps.on.assert_called_once_with(outlet=1)

    def test_power_off(self, mocker, prepare_connection_mocks):
        dli = DLI(connection=prepare_connection_mocks, ip="127.0.0.1", username="admin", password="........")
        mocker.patch.object(dli.wps, "off")

        dli.power_off(outlet_number=4)

        dli.wps.off.assert_called_once_with(outlet=4)

    def test_power_cycle(self, mocker, prepare_connection_mocks):
        dli = DLI(connection=prepare_connection_mocks, ip="127.0.0.1", username="admin", password="........")
        dli.wps.cycle = mocker.Mock()

        dli.power_cycle(outlet_number=3, time_delay=1)

        dli.wps.cycle.assert_called_once_with(outlet=3)

    def test_set_state_on(self, mocker, prepare_connection_mocks):
        dli = DLI(connection=prepare_connection_mocks, ip="127.0.0.1", username="admin", password="........")
        mocker.patch.object(dli, "power_on")

        dli.set_state(state=DliSocketPowerStates.on, outlet_number=4)

        dli.power_on.assert_called_once_with(outlet_number=4)

    def test_set_state_off(self, mocker, prepare_connection_mocks):
        dli = DLI(connection=prepare_connection_mocks, ip="127.0.0.1", username="admin", password="........")
        mocker.patch.object(dli, "power_off")

        dli.set_state(state=DliSocketPowerStates.off, outlet_number=7)

        dli.power_off.assert_called_once_with(outlet_number=7)

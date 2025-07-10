# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
from ipaddress import ip_address

import pytest
from mfd_connect import Connection
from mfd_typing import OSName

from mfd_powermanagement import Ipmi, IpmiStates
from mfd_powermanagement.exceptions import PowerManagementException
from mfd_powermanagement.ipmi import IpmiType, ipmi_ver


@pytest.mark.parametrize("ipmi_type", [IpmiType.IPMIUtil, IpmiType.IPMITool])
class TestIPMI:
    @pytest.fixture()
    def connection(self, mocker):
        conn = mocker.create_autospec(Connection)
        conn.get_os_name.return_value = OSName.LINUX
        return conn

    def test_init_host(self, connection, ipmi_type):
        expected_host = "test_host"
        expected_username = "test_user"
        expected_password = "test_pass"
        ipmi = Ipmi(
            connection=connection,
            host=expected_host,
            username=expected_username,
            password=expected_password,
            ipmi_type=ipmi_type,
        )
        ipmi._connection.execute_command.assert_called_once_with(
            ipmi_ver[ipmi_type], shell=False, expected_return_codes={0, 127, 234}
        )

        # test base init
        assert ipmi._host == expected_host
        assert ipmi._username == expected_username
        assert ipmi._password == expected_password

    def test_init_ip(self, connection, ipmi_type):
        expected_ip = ip_address("10.10.10.10")
        expected_username = "test_user"
        expected_password = "test_pass"
        ipmi = Ipmi(
            connection=connection,
            ip="10.10.10.10",
            username=expected_username,
            password=expected_password,
            ipmi_type=ipmi_type,
        )
        ipmi._connection.execute_command.assert_called_once_with(
            ipmi_ver[ipmi_type], shell=False, expected_return_codes={0, 127, 234}
        )

        # test base init
        assert ipmi._host == expected_ip
        assert ipmi._username == expected_username
        assert ipmi._password == expected_password

    # test base init
    def test_init_failure(self, connection, ipmi_type):
        with pytest.raises(ValueError):
            Ipmi(connection=connection, host="", username="", password="", ipmi_type=ipmi_type)

    def test_init_tool_not_exists(self, connection, ipmi_type):
        connection.execute_command.side_effect = FileNotFoundError
        with pytest.raises(PowerManagementException):
            Ipmi(
                connection=connection,
                ip="10.10.10.10",
                username="expected_username",
                password="expected_password",
                ipmi_type=ipmi_type,
            )

    def test_set_state(self, connection, mocker, ipmi_type):
        process = mocker.Mock()
        process.stdout = "completed successfully"
        connection.execute_command.return_value = process
        process.stderr = ""
        ipmi = Ipmi(
            connection=connection,
            ip="10.10.10.10",
            username="expected_username",
            password="expected_password",
            ipmi_type=ipmi_type,
        )
        ipmi.set_state(state=IpmiStates.up, retry_count=1)
        if ipmi_type == IpmiType.IPMIUtil:
            connection.execute_command.assert_called_with(
                (
                    f"ipmiutil power -F lan2 -N 10.10.10.10 "
                    f"-U expected_username -P expected_password "
                    f"{IpmiStates.up.value['ipmiutil']} -V 4"
                )
            )
        elif ipmi_type == IpmiType.IPMITool:
            connection.execute_command.assert_called_with(
                (
                    f"ipmitool -I lanplus -H 10.10.10.10 "
                    f"-U expected_username -P expected_password "
                    f"chassis power {IpmiStates.up.value['ipmitool']}"
                )
            )

    def test_set_state_failure(self, connection, mocker, ipmi_type):
        process = mocker.Mock()
        process.stdout = "completed unsuccessfully"
        connection.execute_command.return_value = process
        process.stderr = ""
        ipmi = Ipmi(
            connection=connection,
            ip="10.10.10.10",
            username="expected_username",
            password="expected_password",
            ipmi_type=ipmi_type,
        )
        with pytest.raises(PowerManagementException):
            ipmi.set_state(state=IpmiStates.up, retry_count=3)
        # 4 because +1 with retry_count, because of init
        assert connection.execute_command.call_count == 4

    def test_power_up(self, connection, mocker, ipmi_type):
        ipmi = Ipmi(
            connection=connection,
            ip="10.10.10.10",
            username="expected_username",
            password="expected_password",
            ipmi_type=ipmi_type,
        )
        ipmi.set_state = mocker.Mock()
        ipmi.power_up()
        ipmi.set_state.assert_called_once_with(state=IpmiStates.up, retry_count=3)

    def test_power_down(self, connection, mocker, ipmi_type):
        ipmi = Ipmi(
            connection=connection,
            ip="10.10.10.10",
            username="expected_username",
            password="expected_password",
            ipmi_type=ipmi_type,
        )
        ipmi.set_state = mocker.Mock()
        ipmi.power_down()
        ipmi.set_state.assert_called_once_with(state=IpmiStates.down, retry_count=3)

    def test_powercycle(self, connection, mocker, ipmi_type):
        ipmi = Ipmi(
            connection=connection,
            ip="10.10.10.10",
            username="expected_username",
            password="expected_password",
            ipmi_type=ipmi_type,
        )
        ipmi.set_state = mocker.Mock()
        mocker.patch("time.sleep", mocker.Mock())
        ipmi.powercycle()
        ipmi.set_state.assert_any_call(state=IpmiStates.down, retry_count=3)
        ipmi.set_state.assert_any_call(state=IpmiStates.up, retry_count=3)
        assert ipmi.set_state.call_count == 2

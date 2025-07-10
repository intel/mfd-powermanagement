# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
import pytest
from mfd_common_libs import log_levels
from requests import Response

from mfd_powermanagement.ccsg import CCSG, CCSGPowerStates
from mfd_powermanagement.exceptions import PowerManagementException


class TestCCSG:
    @pytest.fixture()
    def ccsg(self):
        yield CCSG("127.0.0.1", "user", "*****")

    def test__login(self, ccsg, mocker):
        response_mock = mocker.Mock()
        response_mock.content = (
            b'<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">'
            b"<soap:Body><ns2:signOnResponse xmlns:ns2="
            b'"http://com.raritan.cc.bl.webservice.service.security/types">'
            b"<result>E2ACCC0D6AB7C481348F37FB070ECD44</result></ns2:signOnResponse></soap:Body></soap:Envelope>"
        )
        ccsg._generic_api_call = mocker.create_autospec(ccsg._generic_api_call, return_value=response_mock)
        ccsg._login()
        assert ccsg.session_id == "E2ACCC0D6AB7C481348F37FB070ECD44"

    def test__login_failure(self, ccsg, mocker):
        ccsg._generic_api_call = mocker.create_autospec(ccsg._generic_api_call, side_effect=PowerManagementException)
        with pytest.raises(PowerManagementException, match="Found problem with login request."):
            ccsg._login()

    def test__logout(self, ccsg, mocker):
        ccsg.session_id = "some id"
        ccsg._generic_api_call = mocker.create_autospec(ccsg._generic_api_call)
        ccsg._logout()
        assert ccsg.session_id is None

    def test__logout_not_required(self, ccsg, mocker):
        ccsg.session_id = None
        ccsg._generic_api_call = mocker.create_autospec(ccsg._generic_api_call)
        ccsg._logout()
        ccsg._generic_api_call.assert_not_called()

    def test___extract_device_id_not_found(self, ccsg, mocker):
        response_mock = mocker.Mock()
        response_mock.content = (
            b'<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body>'
            b'<ns2:getNodeByNameResponse xmlns:ns2="http://com.raritan.cc.bl.webservice.service.node/types"><result>'
            b'<interfacesData><description xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>'
            b"<deviceName>JF3418-18A11-KVM-KX3-01</deviceName>"
            b'<hostname xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            b'xsi:nil="true"/><id>9785</id><ip xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            b'xsi:nil="true"/><name>Cfg-H.18A11.33926.SuperM.N6.P28</name><portID>P_000d5d1d187e_27</portID>'
            b"<portName>Cfg-H.18A11.33926.SuperM.N6.P28</portName><portNumber>28</portNumber><type>Out-of-Band - KVM"
            b"</type></interfacesData><name>Cfg-H.18A11.33926.SuperM.N6.P28</name></result></ns2:getNodeByNameResponse>"
            b"</soap:Body></soap:Envelope>"
        )
        assert ccsg._extract_device_id(response_mock, "power") == []

    def test_extract_device_id(self, ccsg, mocker):
        response_mock = mocker.Mock()
        response_mock.content = (
            b'<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body>'
            b'<ns2:getNodeByNameResponse xmlns:ns2="http://com.raritan.cc.bl.webservice.service.node/types">'
            b"<result></interfacesData><interfacesData><description></description><deviceName>JF3418-18A11-PDUL"
            b'</deviceName><hostname xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>'
            b'<id>11145</id><ip xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            b'xsi:nil="true"/><name>Outlet 31</name><portID>.31</portID><portName>Outlet 31</portName>'
            b"<portNumber>31</portNumber><type>Power Control - Managed Power Strip</type></interfacesData>"
            b"<name>Cfg-H.18A11.34365.WolfP.P9</name></result></ns2:getNodeByNameResponse>"
            b"</soap:Body></soap:Envelope>"
        )
        assert ccsg._extract_device_id(response_mock, "power") == ["11145"]

    def test_extract_device_id_multiple_id(self, ccsg, mocker):
        response_mock = mocker.Mock()
        response_mock.content = (
            b'<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body>'
            b'<ns2:getNodeByNameResponse xmlns:ns2="http://com.raritan.cc.bl.webservice.service.node/types">'
            b"<result><interfacesData><description></description><deviceName>JF3418-1B11-PDUL-1B11K1-P31</deviceName>"
            b'<hostname xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>'
            b'<id>20830</id><ip xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>'
            b"<name>Outlet 12</name><portID>O_PQ12900602_11</portID><portName>Cfg-L.1B11.CoyoteP.35171.P6(1)</portName>"
            b"<portNumber>12</portNumber><type>Power Control - Managed Power Strip</type></interfacesData>"
            b'<interfacesData><description xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>'
            b"<deviceName>JF3418-1B11-KVM-KX3-01</deviceName>"
            b'<hostname xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>'
            b'<id>20806</id><ip xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>'
            b"<name>Cfg-L.1B11.CoyoteP.35171.P6</name><portID>P_000d5d1001ac_5</portID>"
            b"<portName>Cfg-L.1B11.CoyoteP.35171.P6</portName><portNumber>6</portNumber>"
            b"<type>Out-of-Band - KVM</type></interfacesData><interfacesData><description></description>"
            b"<deviceName>JF3418-1B11-PDUR-1B11K1-P32</deviceName>"
            b'<hostname xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>'
            b'<id>20831</id><ip xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>'
            b"<name>Outlet 12</name><portID>O_PQ12900600_11</portID><portName>Cfg-L.1B11.CoyoteP.35171.P6(2)</portName>"
            b"<portNumber>12</portNumber><type>Power Control - Managed Power Strip</type></interfacesData>"
            b"<name>Cfg-L.1B11.CoyoteP.35171.P6</name></result></ns2:getNodeByNameResponse>"
            b"</soap:Body></soap:Envelope>"
        )
        assert ccsg._extract_device_id(response_mock, "power") == ["20830", "20831"]

    def test__gather_power_socket(self, ccsg, mocker):
        ccsg.session_id = "1"
        ccsg._generic_api_call = mocker.Mock()
        ccsg._extract_device_id = mocker.create_autospec(ccsg._extract_device_id, return_value=["11145"])
        assert ccsg._gather_power_socket_id() == "11145"

    def test__gather_power_socket_not_found(self, ccsg, mocker):
        ccsg.session_id = "1"
        ccsg._generic_api_call = mocker.Mock()
        ccsg._extract_device_id = mocker.create_autospec(ccsg._extract_device_id, return_value=[])
        with pytest.raises(Exception):
            ccsg._gather_power_socket_id()

    def test__get_value_from_response(self, ccsg, mocker):
        response_mock = mocker.Mock()
        response_mock.content = (
            b'<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body>'
            b'<ns2:getNodeByNameResponse xmlns:ns2="http://com.raritan.cc.bl.webservice.service.node/types">'
            b"<result><interfacesData><description></description><deviceName>JF3418-1B11-PDUL-1B11K1-P31</deviceName>"
            b'<hostname xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>'
            b'<id>20830</id><ip xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>'
            b"<name>Outlet 12</name><portID>O_PQ12900602_11</portID><portName>Cfg-L.1B11.CoyoteP.35171.P6(1)</portName>"
            b"<portNumber>12</portNumber><type>Power Control - Managed Power Strip</type></interfacesData>"
            b'<interfacesData><description xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>'
            b"<deviceName>JF3418-1B11-KVM-KX3-01</deviceName>"
            b'<hostname xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>'
            b'<id>20806</id><ip xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>'
            b"<name>Cfg-L.1B11.CoyoteP.35171.P6</name><portID>P_000d5d1001ac_5</portID>"
            b"<portName>Cfg-L.1B11.CoyoteP.35171.P6</portName><portNumber>6</portNumber>"
            b"<type>Out-of-Band - KVM</type></interfacesData><interfacesData><description></description>"
            b"<deviceName>JF3418-1B11-PDUR-1B11K1-P32</deviceName>"
            b'<hostname xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>'
            b'<id>20831</id><ip xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>'
            b"<name>Outlet 12</name><portID>O_PQ12900600_11</portID><portName>Cfg-L.1B11.CoyoteP.35171.P6(2)</portName>"
            b"<portNumber>12</portNumber><type>Power Control - Managed Power Strip</type></interfacesData>"
            b"<name>Cfg-L.1B11.CoyoteP.35171.P6</name></result></ns2:getNodeByNameResponse>"
            b"</soap:Body></soap:Envelope>"
        )
        assert (
            ccsg._get_value_from_response(response_mock, key_to_search="type") == "Power Control - Managed Power Strip"
        )

    def test__get_value_from_response_incorrect_structure(self, ccsg, mocker):
        response_mock = mocker.Mock()
        response_mock.content = b'<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"></soap:Body>"'
        with pytest.raises(PowerManagementException, match="Cannot parse response into XML"):
            ccsg._get_value_from_response(response_mock, key_to_search="type")

    def test__get_value_from_response_not_found(self, ccsg, mocker):
        response_mock = mocker.Mock()
        response_mock.content = (
            b'<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"></soap:Envelope>'
        )
        with pytest.raises(PowerManagementException, match="Not found key 'type' in response."):
            ccsg._get_value_from_response(response_mock, key_to_search="type")

    def test_generic_api_call_success(self, ccsg, mocker):
        url = "http://example.com"
        data = "test data"
        mock_response = mocker.create_autospec(Response, instance=True)
        mock_response.status_code = 200
        mock_response.text = "response"
        post_mock = mocker.patch("requests.post", return_value=mock_response)
        response = ccsg._generic_api_call(url, data)
        assert response.text == "response"
        post_mock.assert_called_once_with(
            url,
            data=data,
            headers={"Content-Type": "text/xml"},
            verify=False,
            cert=("/etc/ssl/ccsg/ccsg.crt.pem", "/etc/ssl/ccsg/ccsg.key.pem"),
        )

    def test_generic_api_call_failure(self, ccsg, mocker, caplog):
        caplog.set_level(level=log_levels.MODULE_DEBUG)
        url = "http://example.com"
        data = "test data"
        mock_response = mocker.create_autospec(Response, instance=True)
        mock_response.status_code = 400
        mock_response.text = "Oops"
        mocker.patch("requests.post", return_value=mock_response)
        with pytest.raises(PowerManagementException, match="Response has incorrect status code: 400"):
            ccsg._generic_api_call(url, data)
        assert "Error on Raritan CCSG api call ! Response status code: 400" in caplog.text

    def test_set_state_without_passing_device(self, ccsg, mocker):
        ccsg.device_name = "device"
        ccsg.power_socket_id = "1"
        ccsg.session_id = "1"
        ccsg._generic_api_call = mocker.create_autospec(ccsg._generic_api_call)
        ccsg._gather_power_socket_id = mocker.create_autospec(ccsg._gather_power_socket_id)
        ccsg._login = mocker.create_autospec(ccsg._login)
        ccsg._wait_for_finished_change_state_job = mocker.create_autospec(
            ccsg._wait_for_finished_change_state_job, return_value=["11145"]
        )
        ccsg.set_state(state=CCSGPowerStates.on)
        ccsg._wait_for_finished_change_state_job.assert_called_once_with("device")
        ccsg._gather_power_socket_id.assert_not_called()
        ccsg._login.assert_not_called()

    def test_set_state_with_passing_device(self, ccsg, mocker):
        ccsg.session_id = "1"
        ccsg._generic_api_call = mocker.create_autospec(ccsg._generic_api_call)
        ccsg._gather_power_socket_id = mocker.create_autospec(ccsg._gather_power_socket_id)
        ccsg._login = mocker.create_autospec(ccsg._login)
        ccsg._wait_for_finished_change_state_job = mocker.create_autospec(
            ccsg._wait_for_finished_change_state_job, return_value=["11145"]
        )
        ccsg.set_state(state=CCSGPowerStates.on, device_name="device")
        ccsg._wait_for_finished_change_state_job.assert_called_once_with("device")
        ccsg._gather_power_socket_id.assert_called_once()
        ccsg._login.assert_not_called()

    def test_set_state_no_device(self, ccsg):
        ccsg.device_name = None
        with pytest.raises(
            PowerManagementException, match="Missing device name value, not passed in constructor or method parameter"
        ):
            ccsg.set_state(state=CCSGPowerStates.on)

    def test_power_cycle(self, ccsg, mocker):
        ccsg.set_state = mocker.create_autospec(ccsg.set_state)
        ccsg.power_cycle(device_name="device")
        ccsg.set_state.assert_has_calls(
            [
                mocker.call(state=CCSGPowerStates.off, device_name="device"),
                mocker.call(state=CCSGPowerStates.on, device_name="device"),
            ]
        )

    def test_power_off(self, ccsg, mocker):
        ccsg.set_state = mocker.create_autospec(ccsg.set_state)
        ccsg.power_off(device_name="device")
        ccsg.set_state.assert_called_once_with(state=CCSGPowerStates.off, device_name="device")

    def test_power_on(self, ccsg, mocker):
        ccsg.set_state = mocker.create_autospec(ccsg.set_state)
        ccsg.power_on(device_name="device")
        ccsg.set_state.assert_called_once_with(state=CCSGPowerStates.on, device_name="device")

    def test__wait_for_finished_change_state_job(self, ccsg, mocker):
        mocker.patch("mfd_powermanagement.ccsg.time.sleep")
        response_mock = mocker.Mock()
        response_mock.content = (
            b'<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">'
            b'<soap:Body><ns2:getNodePowerResponse xmlns:ns2="'
            b'http://com.raritan.cc.bl.webservice.service.node/types"><inProgress>false</inProgress>'
            b"</ns2:getNodePowerResponse></soap:Body></soap:Envelope>"
        )
        ccsg._login = mocker.create_autospec(ccsg._login)
        ccsg._generic_api_call = mocker.create_autospec(ccsg._generic_api_call, return_value=response_mock)
        ccsg._get_value_from_response = mocker.create_autospec(ccsg._get_value_from_response, return_value="false")
        ccsg._wait_for_finished_change_state_job("device")

    def test__wait_for_finished_change_state_job_not_finished(self, ccsg, mocker):
        mocker.patch("mfd_powermanagement.ccsg.time.sleep")
        response_mock = mocker.Mock()
        response_mock.content = (
            b'<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">'
            b'<soap:Body><ns2:getNodePowerResponse xmlns:ns2="'
            b'http://com.raritan.cc.bl.webservice.service.node/types"><inProgress>true</inProgress>'
            b"</ns2:getNodePowerResponse></soap:Body></soap:Envelope>"
        )
        ccsg._login = mocker.create_autospec(ccsg._login)
        ccsg._generic_api_call = mocker.create_autospec(ccsg._generic_api_call, return_value=response_mock)
        ccsg._get_value_from_response = mocker.create_autospec(ccsg._get_value_from_response, return_value="true")
        with pytest.raises(PowerManagementException, match="Job is still not finished"):
            ccsg._wait_for_finished_change_state_job("device")

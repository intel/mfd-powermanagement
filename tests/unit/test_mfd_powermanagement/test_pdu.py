# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
import pytest

from mfd_powermanagement import APC, Raritan, PDUStates
from mfd_powermanagement.exceptions import PowerManagementException, PDUConfigurationException, PDUSNMPException


class TestPDU:
    def test_init_apc_oids(self):
        pdu = APC(ip="10.10.10.10")
        assert pdu.OUTLET_CONTROL == "1.3.6.1.4.1.318.1.1.12.3.3.1.1.4"
        assert pdu.ON_COMMAND == "1"
        assert pdu.OFF_COMMAND == "2"
        assert pdu.CYCLE_COMMAND == "3"

    def test_init_raritan_oids(self):
        pdu = Raritan(ip="10.10.10.10")
        assert pdu.OUTLET_CONTROL == "1.3.6.1.4.1.13742.6.4.1.2.1.2.1"
        assert pdu.ON_COMMAND == "1"
        assert pdu.OFF_COMMAND == "0"
        assert pdu.CYCLE_COMMAND == "2"

    def test_set_state_apc_on(self, mocker):
        pdu = APC(ip="10.10.10.10")
        pdu._set_oid = mocker.Mock()
        pdu.set_state(state=PDUStates.on, outlet_number=4)
        pdu._set_oid.assert_called_once_with(oid="1.3.6.1.4.1.318.1.1.12.3.3.1.1.4", instance_number=4, value="1")

    def test_apc_power_on(self, mocker):
        pdu = APC(ip="10.10.10.10")
        pdu.set_state = mocker.Mock()
        pdu.power_on(outlet_number=1)
        pdu.set_state.assert_called_once_with(state=PDUStates.on, outlet_number=1)

    def test_raritan_power_cycle(self, mocker):
        pdu = Raritan(ip="10.10.10.10")
        pdu.set_state = mocker.Mock()
        pdu.power_cycle(outlet_number=3)
        pdu.set_state.assert_called_once_with(state=PDUStates.cycle, outlet_number=3)

    def test_raritan_power_off(self, mocker):
        pdu = Raritan(ip="10.10.10.10")
        pdu.set_state = mocker.Mock()
        pdu.power_off(outlet_number=4)
        pdu.set_state.assert_called_once_with(state=PDUStates.off, outlet_number=4)

    @pytest.fixture
    def pdu(self):
        return APC(ip="1.2.3.4")

    @pytest.fixture(autouse=True)
    def mock_snmp_deps(self, monkeypatch):
        monkeypatch.setattr("mfd_powermanagement.pdu.ObjectIdentity", lambda x: x)
        monkeypatch.setattr("mfd_powermanagement.pdu.CommunityData", lambda x: x)
        monkeypatch.setattr("mfd_powermanagement.pdu.ContextData", lambda: None)
        monkeypatch.setattr("mfd_powermanagement.pdu.ObjectType", lambda *a: a)
        monkeypatch.setattr("mfd_powermanagement.pdu.Integer32", lambda x: x)

    @pytest.fixture
    def mock_logger(self, monkeypatch):
        class DummyLogger:
            def log(self, **kwargs):
                self.called = True

        logger = DummyLogger()
        monkeypatch.setattr("mfd_powermanagement.pdu.logger", logger)
        return logger

    @pytest.fixture
    def mock_sleep(self, monkeypatch):
        called = {}

        def dummy_sleep(seconds):
            called["called"] = True

        monkeypatch.setattr("mfd_powermanagement.pdu.time.sleep", dummy_sleep)
        return called

    @pytest.fixture
    def mock_asyncio_run(self, monkeypatch):
        def fake_asyncio_run(coro, *args, **kwargs):
            # Will be patched per test
            return None

        monkeypatch.setattr("mfd_powermanagement.pdu.asyncio.run", fake_asyncio_run)
        return fake_asyncio_run

    def test_set_oid_success(self, pdu, monkeypatch, mock_logger, mock_sleep, mock_asyncio_run):
        def fake_asyncio_run(coro, *args, **kwargs):
            if "set_transport_target" in str(coro):
                return None
            return (None, None, None, ["oid=val"])

        monkeypatch.setattr("mfd_powermanagement.pdu.asyncio.run", fake_asyncio_run)
        pdu._set_oid(oid="1.2.3", instance_number=1, value="1")
        assert hasattr(mock_logger, "called") or getattr(mock_logger, "called", False)
        assert mock_sleep["called"]

    def test_set_oid_error_indication(self, pdu, monkeypatch, mock_asyncio_run):
        def fake_asyncio_run(coro, *args, **kwargs):
            if "set_transport_target" in str(coro):
                return None
            return ("error", None, None, [])

        monkeypatch.setattr("mfd_powermanagement.pdu.asyncio.run", fake_asyncio_run)
        with pytest.raises(PDUConfigurationException):
            pdu._set_oid(oid="1.2.3", instance_number=1, value="1")

    def test_set_oid_error_status(self, pdu, monkeypatch, mock_asyncio_run):
        class DummyStatus:
            def __str__(self):
                return "snmp error"

            def prettyPrint(self):
                return "snmp error"

            def __bool__(self):
                return True  # Ensure truthy

        def fake_asyncio_run(coro, *args, **kwargs):
            if "set_transport_target" in str(coro):
                return None
            return (None, DummyStatus(), 1, ["oid=val"])

        monkeypatch.setattr("mfd_powermanagement.pdu.asyncio.run", fake_asyncio_run)
        with pytest.raises(PDUSNMPException):
            pdu._set_oid(oid="1.2.3", instance_number=1, value="1")

    def test_init_pdu_community(self):
        pdu = APC(ip="10.10.10.10")
        assert pdu._community_string == "private"
        pdu = APC(ip="10.10.10.10", community_string="string")
        assert pdu._community_string == "string"
        assert pdu._outlet_number is None
        pdu = APC(ip="10.10.10.10", outlet_number=5)
        assert pdu._outlet_number == 5

    def test_set_state_on_with_outlet_number_from_constructor(self, mocker):
        pdu = APC(ip="10.10.10.10", outlet_number=4)
        pdu._set_oid = mocker.Mock()
        pdu.set_state(state=PDUStates.on)
        pdu._set_oid.assert_called_once_with(oid="1.3.6.1.4.1.318.1.1.12.3.3.1.1.4", instance_number=4, value="1")

    def test_set_state_on_with_outlet_number_from_method(self, mocker):
        pdu = APC(ip="10.10.10.10", outlet_number=4)
        pdu._set_oid = mocker.Mock()
        pdu.set_state(state=PDUStates.on, outlet_number=5)
        pdu._set_oid.assert_called_once_with(oid="1.3.6.1.4.1.318.1.1.12.3.3.1.1.4", instance_number=5, value="1")

    def test_set_state_on_without_outlet_number(self, mocker):
        pdu = APC(ip="10.10.10.10")
        pdu._set_oid = mocker.Mock()
        match = "Missing outlet number value, not passed in constructor or method parameter"
        with pytest.raises(PowerManagementException, match=match):
            pdu.set_state(state=PDUStates.on)

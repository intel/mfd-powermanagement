# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Module for controlling Power Distribution Units via SNMP."""

import asyncio
import logging
import time
from abc import ABC
from enum import Enum
from typing import Optional

from mfd_common_libs import add_logging_level, log_levels
from pysnmp.entity.engine import SnmpEngine
from pysnmp.hlapi.v3arch import CommunityData, UdpTransportTarget, ContextData
from pysnmp.hlapi.v3arch.asyncio.cmdgen import set_cmd
from pysnmp.proto.rfc1902 import Integer32
from pysnmp.smi.rfc1902 import ObjectIdentity, ObjectType

from .base import PowerManagement
from .exceptions import PDUConfigurationException, PDUSNMPException, PowerManagementException

logger = logging.getLogger(__name__)
add_logging_level("MODULE_DEBUG", log_levels.MODULE_DEBUG)


class PDUStates(Enum):
    """Available power states for PDU."""

    on = "ON"
    off = "OFF"
    cycle = "CYCLE"


class PDU(PowerManagement, ABC):
    """
    Implementation of Power Distribution Units management via SNMP.

    This is a base class
    for specific vendor implementations (eg. APC, Raritan). Do not instantiate this class.

    Usage example (for derived class):
    >>> power_switch = APC(ip='10.10.10.10')
    >>> power_switch.power_on(outlet_number=5)
    Outlet no. 5 is powered on
    >>>
    >>> power_switch.set_state(state=PDUStates.cycle, outlet_number=2)
    Outlet no. 2 is power cycled.
    """

    def __init__(
        self, *, ip: str, udp_port: int = 161, community_string: str = "private", outlet_number: Optional[int] = None
    ) -> None:
        """
        Init of PDU.

        :param ip: IP address of PDU device.
        :param udp_port: UDP port for SNMP connection. By default it is 161.
        :param community_string: Community to use for SNMP connection, available in configuration of PDU
        :param outlet_number: Optional Outlet number, when want to store it in object of PDU.
        """
        self._transport_target = None
        self._snmp_engine = SnmpEngine()
        self._ip = ip
        self._udp_port = udp_port
        self._community_string = community_string
        self._outlet_number = outlet_number

    def power_off(self, *, outlet_number: Optional[int] = None) -> None:
        """
        Power off the specified outlet.

        :param outlet_number: Number of electrical socket to be controlled, otherwise will be used from object
        :raises PDUConfigurationException: if there is a misconfiguration or timeout eg. wrong IP selected
        :raises PDUSNMPException: if there is an error returned from remote PDU via SNMP eg. wrong value set
        """
        self.set_state(state=PDUStates.off, outlet_number=outlet_number)

    def power_on(self, *, outlet_number: Optional[int] = None) -> None:
        """
        Power on the specified outlet.

        :param outlet_number: Number of electrical socket to be controlled, otherwise will be used from object
        :raises PDUConfigurationException: if there is a misconfiguration or timeout eg. wrong IP selected
        :raises PDUSNMPException: if there is an error returned from remote PDU via SNMP eg. wrong value set
        :raises PowerManagementException: when not passed outlet number
        """
        self.set_state(state=PDUStates.on, outlet_number=outlet_number)

    def power_cycle(self, *, outlet_number: Optional[int] = None) -> None:
        """
        Power cycle the specified outlet. The cycle delay depends on the PDU setting for the outlet.

        :param outlet_number: Number of electrical socket to be controlled, otherwise will be used from object
        :raises PDUConfigurationException: if there is a misconfiguration or timeout eg. wrong IP selected
        :raises PDUSNMPException: if there is an error returned from remote PDU via SNMP eg. wrong value set
        :raises PowerManagementException: when not passed outlet number
        """
        self.set_state(state=PDUStates.cycle, outlet_number=outlet_number)

    def set_state(self, *, state: PDUStates, outlet_number: Optional[int] = None) -> None:
        """
        Set given power state.

        :param state: State to set
        :param outlet_number: Number of electrical socket to be controlled, otherwise will be used from object
        :raises PDUConfigurationException: if there is a misconfiguration or timeout eg. wrong IP selected
        :raises PDUSNMPException: if there is an error returned from remote PDU via SNMP eg. wrong value set
        :raises PowerManagementException: when not passed outlet number
        """
        number = self._outlet_number if self._outlet_number is not None else None
        number = outlet_number if outlet_number is not None else number

        if number is None:
            raise PowerManagementException("Missing outlet number value, not passed in constructor or method parameter")

        self._set_oid(oid=self.OUTLET_CONTROL, instance_number=number, value=getattr(self, f"{state.value}_COMMAND"))

    async def set_transport_target(self, ip: str, udp_port: int) -> None:
        """
        Update UDP transport target for SNMP connection.

        :param ip: IP address of the PDU device
        :param udp_port: UDP port for SNMP connection
        :return: UdpTransportTarget object for SNMP connection
        """
        target = await UdpTransportTarget.create((ip, udp_port))
        self._transport_target = target

    def _set_oid(self, *, oid: str, instance_number: int = 0, value: str = "0") -> None:
        """
        Set OID for remote device by wrapping PySNMP setCmd method. Waits time for execution.

        :param oid: SNMP Object Identifier representing single controllable entity in MIB base
        :param instance_number: Number of instance for specific OID object to be set, eg. outlet number
        :param value: Value to be set for specific OID representing operation to be performed eg. power on.
        :raises PDUConfigurationException: if there is a misconfiguration or timeout eg. wrong IP selected
        :raises PDUSNMPException: if there is an error returned from remote PDU via SNMP eg. wrong value set
        """
        command = ObjectIdentity(f"{oid}.{instance_number}")

        asyncio.run(self.set_transport_target(self._ip, self._udp_port))
        result = asyncio.run(
            set_cmd(
                self._snmp_engine,
                CommunityData(self._community_string),
                self._transport_target,
                ContextData(),
                ObjectType(command, Integer32(int(value))),
            )
        )
        error_indication, error_status, error_index, var_binds = result
        if error_indication:
            raise PDUConfigurationException(f"{error_indication} - check your configuration and network connection")
        elif error_status:
            raise PDUSNMPException(f"{error_status} error occurred for {var_binds[error_index - 1]}")
        else:
            cool_down_time = 2
            logger.log(
                level=log_levels.MODULE_DEBUG,
                msg=f"Command '{var_binds[0]}' received successfully. Waiting for execution {cool_down_time} seconds.",
            )
            time.sleep(cool_down_time)


class APC(PDU):
    """Implementation of PDU for APC (Schneider Electric) vendor."""

    OUTLET_CONTROL = "1.3.6.1.4.1.318.1.1.12.3.3.1.1.4"
    OFF_COMMAND = "2"
    ON_COMMAND = "1"
    CYCLE_COMMAND = "3"


class Raritan(PDU):
    """Implementation of PDU for Raritan (Legrand) vendor."""

    OUTLET_CONTROL = "1.3.6.1.4.1.13742.6.4.1.2.1.2.1"
    OFF_COMMAND = "0"
    ON_COMMAND = "1"
    CYCLE_COMMAND = "2"

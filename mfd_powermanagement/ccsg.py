# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Module for CommandCenter® Secure Gateway."""

import logging
import re
import time
import typing
import xml.etree.ElementTree as ET
from contextlib import ContextDecorator
from enum import Enum
from types import TracebackType
from typing import Optional, List, Union, Type

import requests
from mfd_common_libs import add_logging_level, log_levels

from mfd_powermanagement.base import PowerManagement
from mfd_powermanagement.consts.ccsg import (
    CCSG_XML_DATA_SIGNON,
    CCSG_XML_DATA_SIGNOFF,
    CCSG_XML_DATA_GET_NODE_INFO,
    CCSG_XML_DATA_CHANGE_POWER_STATUS,
    CCSG_XML_DATA_GET_POWER_STATUS,
)
from mfd_powermanagement.exceptions import PowerManagementException

if typing.TYPE_CHECKING:
    from requests import Response
    from pathlib import Path
logger = logging.getLogger(__name__)
add_logging_level("MODULE_DEBUG", log_levels.MODULE_DEBUG)


class CCSGPowerStates(Enum):
    """Power states for CCSG."""

    on = "power on"
    off = "power off"


class CCSG(PowerManagement, ContextDecorator):
    """CCSG class."""

    def __init__(
        self,
        ip: str,
        username: str,
        password: str,
        *,
        device_name: Optional[str] = None,
        cert_path: Optional[Union["Path", str]] = None,
        key_path: Optional[Union["Path", str]] = None,
        verify: bool = False,
    ):
        """
        Initialize CCSG class.

        :param ip: IP address to connect to ccsg server
        :param username: Username for auth
        :param password: Password for auth
        :param device_name: Device name of machine
        :param cert_path: Path to the certificate file
        :param key_path: Path to the key file
        :param verify: Whether to verify the SSL certificate
        """
        self.url = f"https://{ip}:9443/CommandCenterWebServices/"
        self.device_name = device_name
        self.power_socket_id = None
        self.session_id = None
        self.username = username
        self.password = password
        self.cert_pem = "/etc/ssl/ccsg/ccsg.crt.pem" if not cert_path else cert_path
        self.key_pem = "/etc/ssl/ccsg/ccsg.key.pem" if not key_path else key_path
        self.verify = verify
        if self.device_name:
            self.power_socket_id = self._gather_power_socket_id()
        else:
            self.power_socket_id = None

    def __enter__(self) -> "CCSG":
        """
        Login to the CCSG on the beginning of the session.

        :return: Object
        """
        self._login()
        return self

    def __exit__(
        self,
        __exc_type: Type[BaseException] | None,
        __exc_value: BaseException | None,
        __traceback: TracebackType | None,
    ) -> None:
        """Close session."""
        self._logout()

    def _get_value_from_response(self, response: "Response", key_to_search: str) -> Optional[str]:
        """
        Parse response and return value for key.

        Return first found key value.

        :param response: Response object
        :param key_to_search: Key in response
        :return: Value of the key
        :raises PowerManagementException: If not found key in response
        :raises PowerManagementException: If received incorrect structure
        """
        try:
            xml_response = ET.fromstring(response.content)
        except ET.ParseError as e:
            raise PowerManagementException("Cannot parse response into XML") from e
        for xml_item in xml_response.iter(key_to_search):
            return xml_item.text
        raise PowerManagementException(f"Not found key '{key_to_search}' in response.")

    def _generic_api_call(self, url: str, data: str) -> "Response":
        """
        Call generic API for url with data.

        :param url: URL to the API
        :param data: Input data
        :return: Response object
        :raises PowerManagementException: on failure
        """
        response = requests.post(
            url, data=data, headers={"Content-Type": "text/xml"}, verify=self.verify, cert=(self.cert_pem, self.key_pem)
        )
        if response.status_code != 200:
            logger.log(
                level=log_levels.MODULE_DEBUG,
                msg=f"Error on Raritan CCSG api call ! Response status code: {response.status_code} \n"
                f"Response message: {response.content}",
            )
            raise PowerManagementException(f"Response has incorrect status code: {response.status_code}")
        return response

    def _login(self) -> None:
        """
        Login to the CCSG.

        Set session id for future calls.

        :raises PowerManagementException: if response from login is incorrect
        """
        try:
            logger.log(level=log_levels.MODULE_DEBUG, msg=f"Logging in to CCSG using {self.username}")
            response = self._generic_api_call(
                f"{self.url}AuthenticationAndAuthorizationServicePort?wsdl",
                data=CCSG_XML_DATA_SIGNON.format(self.username, self.password),
            )
            self.session_id = self._get_value_from_response(response, "result")
        except PowerManagementException as e:
            raise PowerManagementException("Found problem with login request.") from e

    def _logout(self) -> None:
        """
        Logout from CCSG.

        Do nothing if not logged in.
        """
        if not self.session_id:
            return
        logger.log(level=log_levels.MODULE_DEBUG, msg="Logging out from CCSG")

        self._generic_api_call(
            f"{self.url}AuthenticationAndAuthorizationServicePort?wsdl",
            data=CCSG_XML_DATA_SIGNOFF.format(self.username, self.session_id),
        )
        self.session_id = None

    def _extract_device_id(self, response: "Response", device_type: str) -> List[str]:
        """
        Get device ID for type from response.

        :param response: Response object
        :param device_type: Type of device, e.g. power
        :return: List of device ids
        """
        result = []
        for value in re.finditer("<id>(?P<device_details>.*?)</type>", str(response.content)):
            value = value.group("device_details")
            if device_type in value.lower():
                result.extend([match.group("id") for match in re.finditer("(?P<id>.*?)</id>", value)])
        return result

    def _gather_power_socket_id(self) -> str:
        """
        Get power socket id for controlling PDU.

        :return: ID of power socket
        :raises PowerManagementException: if not found power socket ID.
        """
        if not self.session_id:
            self._login()
        logger.log(level=log_levels.MODULE_DEBUG, msg=f"Gathering power socket ID for {self.device_name}")
        response = self._generic_api_call(
            f"{self.url}NodeManagementServicePort?wsdl",
            data=CCSG_XML_DATA_GET_NODE_INFO.format(self.session_id, self.device_name),
        )
        device_ids = self._extract_device_id(response, "power")
        power_socket = "</arrayOfString_3>\n<arrayOfString_3>".join(device_ids)  # format of list in XML template
        if power_socket:
            logger.log(level=log_levels.MODULE_DEBUG, msg=f"Power socket ID for {self.device_name} is {device_ids}.")
            return power_socket
        raise PowerManagementException(
            "Could not find power socket ID for device, check node name or if the power device is available"
        )

    def set_state(self, *, state: CCSGPowerStates, device_name: Optional[str] = None) -> None:
        """
        Set given power state.

        :param state: State to set
        :param device_name: Name of device which pdu to be controlled, otherwise will be used from object
        :raises PDUConfigurationException: if there is a misconfiguration or timeout eg. wrong IP selected
        :raises PDUSNMPException: if there is an error returned from remote PDU via SNMP eg. wrong value set
        :raises PowerManagementException: when not passed outlet number
        """
        _device_name = self.device_name if self.device_name is not None else None
        _device_name = device_name if device_name is not None else _device_name
        if _device_name is None:
            raise PowerManagementException("Missing device name value, not passed in constructor or method parameter")

        if not self.session_id:
            self._login()

        power_socket_id = self._gather_power_socket_id() if not self.power_socket_id else self.power_socket_id
        logger.log(level=log_levels.MODULE_DEBUG, msg=f"Setting power state for {self.device_name} to {state.value}.")

        self._generic_api_call(
            f"{self.url}NodeManagementServicePort?wsdl",
            data=CCSG_XML_DATA_CHANGE_POWER_STATUS.format(
                self.session_id,
                _device_name,
                power_socket_id,
                state.value,
                f"{state.value}ing {self.device_name}",
            ),
        )
        self._wait_for_finished_change_state_job(_device_name)

    def power_cycle(self, *, device_name: Optional[str] = None) -> None:
        """
        Power cycle the specified outlet. The cycle delay depends on the PDU setting for the outlet.

        :param device_name: Name of device which pdu to be controlled, otherwise will be used from object
        :raises PowerManagementException: if there is a problem with setting state.
        :raises PowerManagementException: when not passed device name

        """
        self.set_state(state=CCSGPowerStates.off, device_name=device_name)
        self.set_state(state=CCSGPowerStates.on, device_name=device_name)

    def power_off(self, *, device_name: Optional[str] = None) -> None:
        """
        Power off the specified outlet.

        :param device_name: Name of device which pdu to be controlled, otherwise will be used from object
        :raises PowerManagementException: if there is a problem with setting state.
        :raises PowerManagementException: when not passed device name
        """
        self.set_state(state=CCSGPowerStates.off, device_name=device_name)

    def power_on(self, *, device_name: Optional[str] = None) -> None:
        """
        Power on the specified outlet.

        :param device_name: Name of device which pdu to be controlled, otherwise will be used from object
        :raises PowerManagementException: if there is a problem with setting state.
        :raises PowerManagementException: when not passed device name

        """
        self.set_state(state=CCSGPowerStates.on, device_name=device_name)

    def _wait_for_finished_change_state_job(self, device_name: str) -> None:
        """
        Wait for finished job.

        Check 10 times with 10 sec of delay.

        :param device_name: Device name of machine
        :raises PowerManagementException: when job is still running after expected time.
        """
        wait_time = 10
        checks = 10
        if not self.session_id:
            self._login()
        logger.log(
            level=log_levels.MODULE_DEBUG,
            msg=f"Waiting {wait_time*checks}s for finishing set of state for {device_name}.",
        )
        for _ in range(checks):
            response = self._generic_api_call(
                f"{self.url}NodeManagementServicePort?wsdl",
                CCSG_XML_DATA_GET_POWER_STATUS.format(self.session_id, device_name),
            )
            power_in_progress = self._get_value_from_response(response, "inProgress")
            if power_in_progress.casefold() == "false":
                break
            logger.log(
                level=log_levels.MODULE_DEBUG, msg=f"Operation in progress ! Checking again in {wait_time} seconds ..."
            )
            time.sleep(wait_time)
        else:
            logger.log(level=log_levels.MODULE_DEBUG, msg="Too many retries performed, Aborting the operation !")
            raise PowerManagementException("Job is still not finished")
        logger.log(level=log_levels.MODULE_DEBUG, msg=f"Setting power state for {device_name} finished.")

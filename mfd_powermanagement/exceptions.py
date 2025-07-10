# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Module for module exceptions."""


class PowerManagementException(Exception):
    """Handling Power Management exceptions."""


class PDUConfigurationException(PowerManagementException):
    """Exception for PDU configuration errors e.g. networking issues, SNMP protocol turned off."""


class PDUSNMPException(PowerManagementException):
    """Exception for errors returned from remote device e.g. incorrect OID, wrong value set."""


class OSNotSupported(PowerManagementException):
    """Exception for not supported OS."""

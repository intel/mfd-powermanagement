# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Module for powermanagement data structures."""

from enum import Enum


class SystemPowerState(Enum):
    """Enum for System power states."""

    S0 = "on"
    S1 = "standby"
    S3 = "mem"
    S4 = "disk"
    S5 = "off"

# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT

import logging

from mfd_connect import RPyCConnection
from mfd_powermanagement import SystemPowerManagement
from mfd_powermanagement.data_structures import SystemPowerState

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

system_pm = SystemPowerManagement(connection=RPyCConnection("10.10.10.10"))
logger.log(level=logging.DEBUG, msg=f"Available power states: {system_pm.get_available_power_states()}")

system_pm.set_state(state=SystemPowerState.S5)

# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT

import time

from mfd_powermanagement import DLI, DliSocketPowerStates
from mfd_connect import LocalConnection

# connect to the power switch using the specified IP, username and password
powerswitch = DLI(connection=LocalConnection(), ip='10.10.10.10', username='admin', password='*****')

# power off outlet no. 3
powerswitch.power_off(outlet_number=3)

# power on outlet no. 3
powerswitch.power_on(outlet_number=3)

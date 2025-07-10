# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT

import time

from mfd_powermanagement import PDUStates, APC

# create APCSNMP instance using specified IP address and default UDP port 161
power_management = APC(ip="10.10.10.10")
# create instance with custom community string
power_management2 = APC(ip="10.10.10.10", community_string="<string>")
# create instance with outlet number
power_management2 = APC(ip="10.10.10.10", outlet_number=5)


# power off outlet no. 3
power_management.power_off(outlet_number=3)

# power off outlet no. 5 from object
power_management2.power_off()

time.sleep(5)

# power on outlet no. 3 using PDUStates
power_management.set_state(state=PDUStates.on, outlet_number=3)

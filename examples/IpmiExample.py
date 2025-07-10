# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT

from mfd_powermanagement import Ipmi
from mfd_powermanagement.ipmi import IpmiType

# by IP
power_management = Ipmi(ip="10.10.10.10", username="root", password="*****", ipmi_type=IpmiType.IPMITool)
# by HOST
# power_management = Ipmi(host="host.com", username='root', password='*****')

power_management.powercycle()

# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT

import logging

from mfd_powermanagement import CCSG

logging.basicConfig(level=logging.DEBUG)

# possible to pass device in constructor parameters
ccsg = CCSG(
    "ccsg_ip",
    "user",
    "*****",
    device_name="machine_name",
    cert_path=r"C:\Users\user\Downloads\ccsg.crt.pem.or",
    key_path=r"C:\Users\user\Downloads\ccsg.key.pem.or",
)
ccsg.power_cycle()

# to use with more than one machine
ccsg = CCSG(
    "ccsg_ip",
    "user",
    "*****",
    cert_path=r"C:\Users\user\Downloads\ccsg.crt.pem.or",
    key_path=r"C:\Users\user\Downloads\ccsg.key.pem.or",
)
ccsg.power_cycle(device_name="machine_name")
ccsg.power_cycle(device_name="another_machine_name")

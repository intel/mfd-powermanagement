# CCSG
**Module for controlling power switching devices via CCSG API**

**Requires appropriate configuration:**
- generated server certificate for authentication of API (certificate and key files)

## Usage
```python
from mfd_powermanagement import CCSG, CCSGPowerStates
import logging

logging.basicConfig(level=logging.DEBUG)

# possible to pass device in constructor parameters
ccsg = CCSG(
    "ccsg_ip",
    "user",
    "*****",
    device_name="machine_name",
    cert_path=r"C:\Users\user\Downloads\ccsg.crt.pem",
    key_path=r"C:\Users\user\Downloads\ccsg.key.pem",
)
ccsg.set_state(state=CCSGPowerStates.off)
```

## Implemented methods in CCSG

Constructor of CCSG has `device_name` argument, which will be used if `device_name` in methods won't be passed.

`device_name` from methods has priority over value in object.

All the devices inherit from the PDU abstract class which supports the following methods:

`power_off(*, device_name: Optional[str] = None) -> None` - shut down the power of the specified device

`power_on(*, device_name: Optional[str] = None) -> None` - turn on the power of the specified device

`power_cycle(*, device_name: Optional[str] = None) -> None` - shut down and then turn on the power of the specified device (delay configured by the device)

`set_state(*, state: CCSGPowerStates, device_name: Optional[str] = None) -> None` - set any of the available states (`on`, `off`, `cycle`) for the specified outlet

API is raising exception when device_name is not passed anywhere.
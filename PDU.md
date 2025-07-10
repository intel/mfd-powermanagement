# PDU
**Module for controlling power switching devices via SNMP**\
**Requires appropriate configuration of the remote SNMP device:**
- SNMP v1/v2c enabled
- Write or Read/Write community string passed to constructor, default `private` (community string means string used for connecting to PDU via SNMP, available in configuration of PDU)

## Usage
```python
from mfd_powermanagement import PDUStates, APC

pdu = APC(ip='10.10.10.10', community_string="string")

pdu.power_off(outlet_number=1)
pdu.set_state(state=PDUStates.on, outlet_number=3)
```

## Supported devices
Currently, the following devices are supported:
- `APC`
- `Raritan`

## Implemented methods in PDU

Constructor of PDU has `outlet_number` argument, which will be used if `outlet_number` in methods won't be passed.

`outlet_number` from methods has priority over value in object.

All the devices inherit from the PDU abstract class which supports the following methods:\

`power_off(outlet_number: Optional[int]) -> None` - shut down the power of the specified outlet

`power_on(outlet_number: Optional[int]) -> None` - turn on the power of the specified outlet

`power_cycle(outlet_number: Optional[int]) -> None` - shut down and then turns the power of the specified outlet (delay configured by the device)

`set_state(state: PDUStates, outlet_number: Optional[int]) -> None` - set any of the available states (`on`, `off`, `cycle`) for the specified outlet

API is raising exception when outlet_number is not passed anywhere.
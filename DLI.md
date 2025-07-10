# DLI
**Module for controlling Digital Loggers power switching devices**\

## Usage
```python
from mfd_powermanagement import DLI, DliSocketPowerStates

pdu = DLI(connection=LocalConnection(), ip='10.10.10.10', username='admin', password='*****')

pdu.power_off(outlet_number=1)
```

## Implemented methods in DLI
`power_off(outlet_number: int) -> bool` - shuts down the power of the specified outlet

`power_on(outlet_number: int) -> bool` - turns on the power of the specified outlet

`power_cycle(outlet_number: int) -> bool` - shuts down and then turns the power of the specified outlet


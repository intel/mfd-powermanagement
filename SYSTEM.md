# SYSTEM
**Module for controlling power by system commands.**

## Usage
```python
from mfd_connect import RPyCConnection
from mfd_powermanagement import SystemPowerManagement
from mfd_powermanagement.data_structures import SystemPowerState

system_pm = SystemPowerManagement(connection=RPyCConnection("10.10.10.10"))
system_pm.set_state(state=SystemPowerState.S5)
```

**SystemPowerState is a base class, which will detect OS, initialize and return proper class.**

## Implemented methods in SystemPowerManagement

[Linux, FreeBSD, Windows]\
`set_state(self, state: SystemPowerState) -> None` - Set given power state.

[Linux, FreeBSD]\
`get_available_power_states(self) -> List[SystemPowerState]` - Get available power states.

#### Ipmi
**Requires ipmiutil or ipmitool installed on controller and added to PATH environment.**
**At the moment, for Windows supported version is **3.1.3 (tool reports 3.13)****
##### Initialization:

`Ipmi(ip_address: str, user: str, password: str, ipmi_type: IpmiType)`

##### Implemented methods in Ipmi
`powercycle() -> None` - power off, waiting 10 seconds and power on

`power_down() -> None` - shutting down power

`power_up() -> None` - turning on machine

`set_state(state: IpmiStates, retry_count: int) -> None`  - Set given power state. Cannot set state, which is already set.

##### Available `States`:

`up`
`down`
`reset`
`cycle`
`soft`

##### Usage
```python
# local execution
# by IP
ipmi = Ipmi(ip='10.10.10.10', username='root', password='*****')
# by HOST
ipmi = Ipmi(host='idrac.company.com', username='root', password='******')


# remote execution
from mfd_connect import SSHConnection
connection = SSHConnection(ip='10.10.10.0', username='admin', password='*****')
ipmi = Ipmi(connection=connection,ip='10.10.10.10', username='root', password='*****', ipmi_type=IpmiType.IPMITool)
ipmi.powercycle()
ipmi.power_down()
```
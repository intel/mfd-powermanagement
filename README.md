> [!IMPORTANT] 
> This project is under development. All source code and features on the main branch are for the purpose of testing or evaluation and not production ready.

# PowerManagement

Module for managing power (Raritan, APC, Digital Loggers, ipmi, etc. [powercycle, power off, reset])

### How to use

Install module and from module import eg.`Ipmi`

Initialization:

```python
PowerManagement(connection, host, ip, username, password)
```
`host` and `ip` can be used interchangeably. 
`connection` is an object from `mfd_connect` and is used for remote execution

Attributes:

`States` - enums are defined for every tool, so `IpmiStates`
___
### Implemented tools:

[Ipmi](IPMI.md) - implemented controlling via IPMITool and IPMIUtil\
[PDU](PDU.md) - controlling power switch devices via SNMP\
[DLI](DLI.md) - controlling Digital Loggers power switch devices\
[CCSG](CCSG.md) - controlling power switch devices via CCSG\
[SYSTEM](SYSTEM.md) - controlling power via system calls
___

### Implemented methods
Every class that inherits from `PowerManagement` (`IPMI`, `PDU`, `CCSG`) overrides this abstract method:

`set_state(**kwargs) -> bool` - setting wanted state from available states

Methods are described for each implemented tool individually in theirs README.

---

## OS supported:

* WINDOWS
* LNX
* FREEBSD
* ESXI

## Issue reporting

If you encounter any bugs or have suggestions for improvements, you're welcome to contribute directly or open an issue [here](https://github.com/intel/mfd-powermanagement/issues).

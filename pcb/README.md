# PCB files
This folder contains the schematic and gerber files to produce your own modchip PCB.
We ordered our modchip PCB from JLCPCB and selected a PCB thickness of 0.8mm, 1.6mm might work but is not tested. 

An interactive BOM is [provided](./ibom.html), the main active components on the PCB are:
* RaspberryPi RP2040 microcontroller
* W25Q128JVS Flash storage
* MCP1405 MOSFET driver
* Vishay SISS54DN-T1-GE3 Capacitor switching MOSFET
* Vishay SISH112DN-T1-GE3 Crowbar MOSFET
* NLSV1T34 Level shifter
* NCP1117 SOT223 3.3V voltage regulator

At the the time of writing most of these components appear to be available or easily replaceable.
The cost for all components on the PCB at low volume should be less than 25 EUR.

## Optional improvements before building the PCB
* Add a pull-down resistor on the `IN A` pin of the MCP1405 MOSFET driver.
* Modify the locations of the castellated holes in `interposer_footprint.kicad_mod`. Currently the rightmost castellated holes are not conveniently located, see the mounting instructions.
* Do some additional routing such that the RP2040 can monitor eMMC D0 and UART at the same time.
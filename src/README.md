## Modchip software

The firmware for the RP2040 microcontroller can be found in the `modchipfw` folder. You can compile this by running the following commands from within the `modchipfw` folder:

```
mkdir build && cd build
cmake ..
make
```

To update the firmware on the RP2040 you can simply press the button on the modchip before plugging it in. It should now enumerate as a removable disk, copy the `utglitcher.uf2` to this removable disk to update the firmware.

## Host Python software
In the Python folder you can find `pulsegen.py`, this file contains the `PicoPulseGen` class that handles communication with the modchip.
The `example.py` script is a basic example to demonstrate how you can interact with the modchip and how you can set glitch parameters. 
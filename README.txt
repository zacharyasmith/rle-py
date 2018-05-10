For any updates to the codebase, run `sudo ./install.sh`. There will be an executable in the menu bar.
This can then be linked to the desktop.

To manually use the test system, run `./main.py -h`. This is useful for ad-hoc tests that do not use
the entire test suite.

To manually use the PCBs to change the state of the circuit, run the following in a `python3` console:
>>> from components.GPIO import GPIO
>>> gpio=GPIO()
>>> gpio.stage(GPIO.BOARD, 0)
>>> gpio.stage(GPIO.RS485, 0)
>>> gpio.stage(GPIO.LENGTH_EMULATOR, 0)
>>> gpio.stage(GPIO.SHORT_EMULATOR, 0)
>>> gpio.commit()
The above was an example. The GPIO library MUST be committed after a stage.

To use the RS232 terminal along with the GPIO library, open up PuTTY and open a serial comm link
with `/dev/rleRS232` as the serial line (there should be a profile by default).

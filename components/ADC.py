"""
components/ADC.py

Author:
    Zachary Smith
"""
import logging
import time
import Adafruit_ADS1x15

_LOGGER = logging.getLogger()


def read(pin, gain=1):
    """
    Read the ADC values.

    Args:
        pin: Pin number [0-3]

    Returns:
        Float average
    """
    adc = Adafruit_ADS1x15.ADS1015()
    val = adc.read_adc(pin, gain)
    return val


if __name__ == "__main__":
    while True:
        signal_max = 0
        signal_min = 4095
        start = time.time()
        while time.time() - start < 0.5:
            val = read(0, 2)
            if val > signal_max:
                signal_max = val
            if val < signal_min:
                signal_min = val
        pp = signal_max - signal_min
        if signal_max > 1700:
            print("Max {}, Min {}, V {}".format(signal_max, signal_min, (pp * 3.3)/4095))

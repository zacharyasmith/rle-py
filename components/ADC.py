"""
components/ADC.py

Author:
    Zachary Smith
"""
import logging
import time

_LOGGER = logging.getLogger()

try:
    import Adafruit_ADS1x15
except ModuleNotFoundError:
    _LOGGER.error("Functionality will not work for ADC (I2C).")

# 2/3 = +/-6.144V
#   1 = +/-4.096V
#   2 = +/-2.048V
#   4 = +/-1.024V
#   8 = +/-0.512V
#  16 = +/-0.256V


def translate(value, gain) -> float:
    """
    Translates read value into voltage

    Args:
        value: float
        gain: float (see above)

    Returns:
        float voltage
    """
    ratio = value / 0x7FF
    if gain == 2/3:
        return ratio * 6.144
    if gain == 1:
        return ratio * 4.096
    if gain == 2:
        return ratio * 2.048
    if gain == 4:
        return ratio * 1.024
    if gain == 8:
        return ratio * 0.512
    if gain == 16:
        return ratio * 0.256


def read(pin, gain=1):
    """
    Read the ADC values.

    Args:
        pin: Pin number [0-3]
        gain: value (see above)

    Returns:
        Float value
    """
    adc = Adafruit_ADS1x15.ADS1015()
    val = 0
    translated = 0
    for i in range(10):
        raw = adc.read_adc(pin, gain)
        val += raw
        translated += translate(raw, gain)
    val = val / 10
    translated = translated / 10
    _LOGGER.debug('ADC::read:: Pin {}; Raw {}; Translated (gain {}) {} V'.format(pin, val, gain, translated))
    return translated


def read_diff(gain=1):
    """
    Read the ADC across 0-1

    Args:
        gain: value (see above)

    Returns:
        Float value
    """
    adc = Adafruit_ADS1x15.ADS1015()
    translated = 0
    val = 0
    for i in range(10):
        raw = adc.read_adc_difference(0, gain=gain)
        val += raw
        translated += translate(raw, gain)
    translated = translated / 10
    val = val / 10
    _LOGGER.debug('ADC::read_diff:: Raw {}; Translated (gain {}) {} V'.format(val, gain, translated))
    return translated


if __name__ == "__main__":
    while True:
        signal_max = 0
        signal_min = 4095
        start = time.time()
        while time.time() - start < 0.5:
            val = read(0, 1)
            if val > signal_max:
                signal_max = val
            if val < signal_min:
                signal_min = val
        pp = signal_max - signal_min
        if signal_max > 855:
            print("Max {}, Min {}, V {}".format(signal_max, signal_min, (pp * 3.3)/4095))

"""
components/ADC.py

Author:
    Zachary Smith
"""
import logging
import time
import Adafruit_ADS1x15

_LOGGER = logging.getLogger()


class ADC(object):
    """
    Class ADC handles communication with the I2C attached A/D converter
    """

    def __int__(self):
        self.__adc = Adafruit_ADS1x15.ADS1015()
        self.__gain = 1

    def read(self, pin):
        """
        Read the ADC values.

        Args:
            pin: Pin number [0-3]

        Returns:
            Float average
        """
        return self.__adc.read_adc(pin, self.__gain)


if __name__ == "__main__":
    signal_max = 0
    signal_min = 4095
    adc = ADC()
    while True:
        read = adc.read(0)
        if read > signal_max:
            signal_max = read
        elif read < signal_min:
            signal_min = read
        time.sleep(0.25)
        print("Max {}, Min {}".format(signal_max, signal_min))

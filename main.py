"""
main.py

Author:
    Zachary Smith
"""
import logging
import argparse
from components.LD5200Tester import LD5200Tester
from components.LD2100Tester import LD2100Tester
from components.GPIO import GPIO
from view.MainWindow import MainWindow

if __name__ == "__main__" and False:
    ui = MainWindow()
    print("here")

if __name__ == "__main__":
    # argument parser
    parser = argparse.ArgumentParser(description='RLE LD Board Tester.')
    # verbosity
    parser.add_argument('--verbose', '-v', action='count',
                        help='Counts number of `v`s in flag. More flags is more verbose.')
    args = vars(parser.parse_args())
    if args['verbose']:
        if args['verbose'] >= 2:
            logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        elif args['verbose'] == 1:
            logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    gpio = GPIO()
    # gpio.stage(GPIO.BOARD, state=0)
    # gpio.stage(GPIO.RS485, state=0)
    # gpio.commit()
    # _BOARD0 = LD2100Tester(serial='LD2100_BOARD0', mac='00:25:96:FF:FE:12:34:57')
    # _BOARD0.test(gpio, ip_address='10.0.0.189')
    # print(_BOARD0.results())
    gpio.stage(GPIO.BOARD, state=3)
    gpio.commit()
    _BOARD1 = LD5200Tester(serial='LD5200_BOARD1', mac='00:25:96:FF:FE:12:34:56')
    _BOARD1.test(gpio, ip_address='10.0.0.188')
    print(_BOARD1.results())

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


def start() -> None:
    # argument parser
    parser = argparse.ArgumentParser(description='RLE LD Board Tester.')
    # verbosity
    parser.add_argument('--verbose', '-v', action='count',
                        help='Counts number of `v`s in flag. More flags is more verbose.')
    args = vars(parser.parse_args())
    if args['verbose']:
        if args['verbose'] >= 2:
            logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')
        elif args['verbose'] == 1:
            logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')


if __name__ == "__main__":
    start()
    gpio = GPIO()
    gpio.stage(GPIO.BOARD, state=0)
    gpio.commit()
    #_BOARD0 = LD2100Tester(serial='LD2100_BOARD0', mac='00:25:96:FF:FE:12:34:57')
    #_BOARD0.test(gpio, ip_address='10.0.0.189')
    #print(_BOARD0.results())
    _BOARD1 = LD5200Tester(serial='LD5200_BOARD1', mac='00:25:96:FF:FE:12:34:56')
    _BOARD1.test(gpio, ip_address='10.0.0.188')
    print(_BOARD1.results())

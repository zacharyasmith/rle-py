#!/usr/bin/env python3
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
from components.LDBoardTester import LDBoardTester


def start():
    # argument parser
    parser = argparse.ArgumentParser(description='RLE LD Board Tester.')
    # verbosity
    parser.add_argument('--verbose', '-v', action='count',
                        help='Counts number of `v`s in flag. More flags is more verbose.')
    parser.add_argument('board', help='Board selector (LD5200 | LD2100) ')
    parser.add_argument('port', type=int, help='Port (0-2 for LD5200, 3-5 for LD2100)')
    parser.add_argument("--all", help="Run all tests", action="store_true")
    parser.add_argument("--rs232", help="RS232 test", action="store_true")
    parser.add_argument("--length", help="Length detection", action="store_true")
    parser.add_argument("--short", help="Short detection", action="store_true")
    parser.add_argument("--rs485", help="RS485 test", action="store_true")
    parser.add_argument("--eth", help="Ethernet assignment test", action="store_true")
    parser.add_argument("--led", help="LED test", action="store_true")
    parser.add_argument("--current", help="4-20mA test (LD5200 only)", action="store_true")
    parser.add_argument("--relay", help="Relay test", action="store_true")
    args = vars(parser.parse_args())
    if args['verbose']:
        if args['verbose'] >= 2:
            logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')
        elif args['verbose'] == 1:
            logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
    return args


if __name__ == "__main__":
    args = start()
    if args['board'] == LDBoardTester.LD5200 and 0 <= args['port'] <= 2:
        board = LDBoardTester.LD5200
    elif args['board'] == LDBoardTester.LD2100 and 3 <= args['port'] <= 5:
        board = LDBoardTester.LD2100
    else:
        raise Exception('Args usage error. Try [-h] help.')
    gpio = GPIO()
    gpio.stage(GPIO.BOARD, state=args['port'])
    gpio.commit()
    if board == LDBoardTester.LD2100:
        _BOARD0 = LD2100Tester(serial='LD2100_BOARD0', mac='00:25:96:FF:FE:12:34:57')
        _BOARD0.test(gpio, '10.0.0.189', args)
        print(_BOARD0.results())
    elif board == LDBoardTester.LD5200:
        _BOARD1 = LD5200Tester(serial='LD5200_BOARD1', mac='00:25:96:FF:FE:12:34:56')
        _BOARD1.test(gpio, '10.0.0.188', args)
        print(_BOARD1.results())

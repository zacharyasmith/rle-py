"""
main.py

Author:
    Zachary Smith
"""
import logging
import argparse
from components.LD5200Tester import LD5200Tester
from view.MainWindow import MainWindow

if __name__ == "__main__":
    ui = MainWindow()
    print("here")

if __name__ == "__main__" and False:
    # argument parser
    parser = argparse.ArgumentParser(description='RLE LD Board Tester.')
    # verbosity
    parser.add_argument('--verbose', '-v', action='count', help='Counts number of `v`s in flag. More flags is more verbose.')
    args = vars(parser.parse_args())
    if args['verbose']:
        if args['verbose'] >= 2:
            logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        elif args['verbose'] == 1:
            logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    _BOARD = LD5200Tester()
    _BOARD.test()
    print(_BOARD.results())

"""
main.py

Author:
    Zachary Smith
"""
import logging
from components.LD5200Tester import LD5200Tester

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


if __name__ == "__main__":
    _BOARD = LD5200Tester()
    _BOARD.test()
    print(_BOARD.results())

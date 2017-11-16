from components.LD5200Tester import LD5200Tester

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

board1 = LD5200Tester()
board1.test()
print(board1.results())

from components.Exceptions import ConnectionRefusalException
from components.LDBoardTester import LDBoardTester
from time import sleep

try:
    with LDBoardTester() as ld:
        ld.test_datetime_set()
        ld.test_startup_sequence()
        ld.test_voltage()
        print('Sleeping for 3 seconds...')
        sleep(3)
        ld.test_datetime_read()
except ConnectionRefusalException:
    print("Connection refused.")
    exit(1)

from components.Serial import Serial
import re

class LDBoardTester:

    __serial = None

    def __init__(self):
        """Constructor."""
        self.__serial = Serial('/dev/ttyUSB0')

    def test_voltage(self):
        """Test internal voltage is within allowed voltage range."""
        print('LDBoardTester:: Testing 15v supply.')
        response = self.__serial.read_stop(b'15v\n', regex=r'15V Supply:')
        # 15V Supply: 15.1V\r\n
        match = re.search(r'(?:15V Supply: )(\d+(?:\.\d+)?)', str(response))
        if match:
            voltage = float(match.group(1))
            print('LDBoardTester:: Voltage is', voltage)
            if abs(15 - voltage) < 0.5:
                print('LDBoardTester:: Test passed. Within 500 mV.')
                return True
            else:
                print('LDBoardTester:: Test failed. Not within 500 mV.')
                return False
        else:
            print('Nope...')


ld = LDBoardTester()
ld.test_voltage()

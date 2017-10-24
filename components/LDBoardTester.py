from components.Exceptions import OperationsOutOfOrderException
from components.Serial import Serial
import re
import datetime
from time import sleep

class LDBoardTester:
    __serial = None
    __date_set = None

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
        print('LDBoardTester:: Test failed. Not within 500 mV.')
        return False

    def test_datetime_set(self):
        """Test the clock setting mechanism. Best if done initially and checking the time later."""
        self.__date_set = datetime.datetime.today()
        # date 01/01/17
        date = b'date '
        date += bytearray(self.__date_set.strftime("%x"), 'utf8')
        date += b'\n'
        # time 12:00:00
        time = b'time '
        time += bytearray(self.__date_set.strftime("%X"), 'utf8')
        time += b'\n'
        print("LDBoardTester:: Testing datetime setting.")
        self.__serial.read_stop(date, regex=r'ok')
        self.__serial.read_stop(time, regex=r'ok')
        # implies regex succeeded
        return True

    def test_datetime_read(self):
        """Test the clock read mechanism."""
        # Response should be 01/01/17 12:00:00
        if not self.__date_set:
            raise OperationsOutOfOrderException
        print("LDBoardTester:: test_datetime_read:: Testing datetime reading.")
        result = self.__serial.read_stop(b'time\n', regex=self.__date_set.strftime("%x"))
        match = re.search(r'(\d{2}/\d{2}/\d{2})\s+(\d{2}:\d{2}:\d{2})', str(result))
        if match:
            time, date = match.group(1), match.group(2)
            print("LDBoardTester:: test_datetime_read:: Read datetime as {} {}".format(date, time))
            print("LDBoardTester:: test_datetime_read:: Current datetime is {}".format(datetime.datetime.now()
                                                                                       .strftime("%X %x")))
            # parse datetime
            dt = datetime.datetime.strptime("{} {}".format(date, time), "%X %x")
            elapsed = dt - datetime.datetime.now()
            print("LDBoardTester:: test_datetime_read:: Elapsed:", elapsed.total_seconds())
            # seconds allowed to be off by
            allowance = 2
            if elapsed > datetime.timedelta(seconds=allowance):
                print("LDBoardTester:: test_datetime_read:: Failure. Time difference is greater than {} seconds."
                      .format(allowance))
                return False
            # else
            return True
        else:
            print("LDBoardTester:: test_datetime_read:: Expecting (\d{2}/\d{2}/\d{2})\s+(\d{2}:\d{2}:\d{2}) got ",
                  str(result))
            return False


ld = LDBoardTester()
ld.test_datetime_set()
ld.test_voltage()
sleep(3)
ld.test_datetime_read()

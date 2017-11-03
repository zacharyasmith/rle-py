import pymodbus
import serial
from pymodbus.pdu import ModbusRequest
from pymodbus.client.sync import ModbusSerialClient
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.transaction import ModbusRtuFramer


class ModBus:

    __serial_client = None
    __device_file = None
    __tcp_client = None
    __is_serial = None

    def __init__(self, method, device_file="", host=""):
        """
        Initializes modbus communication

        :param method: serial|tcp
        :param device_file: e.g. /dev/ttyUSB0
        :param host: e.g. 10.0.0.1
        """
        connection = False
        if method == "serial":
            self.__is_serial = True
            self.__device_file = device_file
            self.__serial_client = ModbusSerialClient(method="rtu", port=device_file, baudrate=9600, timeout=0)
            connection = self.__serial_client.connect()
        if method == "tcp":
            self.__is_serial = False
            self.__tcp_client = ModbusTcpClient(host=host)
            connection = self.__tcp_client.connect()
        print("ModBus::__init__:: Connection status:", connection)

    def close(self):
        if self.__is_serial:
            self.__serial_client.close()
            print('ModBus::close:: Closing connection with', self.__device_file)

    def read_input_registers(self, address, count=1, unit=0x02):
        """
        Reads and returns modbus register.

        :param address: Starting numerical modbus register address.
        :param count: Number of registers.
        :param unit: Slave address.
        :return: Returns object(s).
        """
        if self.__is_serial:
            ret_val = self.__serial_client.read_input_registers(address, count, unit=unit)
            # ret_val = self.__serial_client.read_holding_registers(address, count, unit=unit)
            return ret_val

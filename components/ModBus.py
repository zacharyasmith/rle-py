"""
components/ModBus.py

Author:
    Zachary Smith
"""
import logging
from pymodbus.client.sync import ModbusSerialClient
from pymodbus.client.common import ReadHoldingRegistersResponse


_LOGGER = logging.getLogger()


class ModBus(object):
    """
    Class ModBus has methods for sending and receiving ModBus commands over serial or TCP
    """

    __serial_client = None
    __device_file = None

    def __init__(self, device_file="", timeout=5):
        """
        Initializes modbus communication

        Args:
            device_file: e.g. /dev/ttyUSB0
            timeout: seconds
        """
        self.__device_file = device_file
        self.__serial_client = ModbusSerialClient(method="rtu", port=device_file, baudrate=9600,
                                                  timeout=timeout)
        connection = self.__serial_client.connect()
        _LOGGER.debug("ModBus:: Connection status with {} : {}".format(self.__device_file, connection))

    def close(self):
        """
        Closes connection
        """
        _LOGGER.debug('ModBus::close:: Closing connection with {}'.format(self.__device_file))
        self.__serial_client.close()

    def read_holding_registers(self, address: int, count=2, unit=0x02) -> ReadHoldingRegistersResponse:
        """
        Reads and returns modbus register.

        Args:
            address: Starting numerical modbus register address.
            count: Number of registers.
            unit: Slave address.

        Returns:
            Returns object(s).
        """
        a = self.__serial_client.read_holding_registers(address, count, unit=unit)
        if type(a) == ReadHoldingRegistersResponse:
            _LOGGER.debug('ModBus::read_holding_registers:: Response: {}'.format(a.registers))
        else:
            _LOGGER.debug('ModBus::read_holding_registers:: Failed. {}'.format(a))
            return False
        return a

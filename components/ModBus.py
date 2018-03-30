"""
components/ModBus.py

Author:
    Zachary Smith
"""
import logging
import socket
import fcntl
import struct
from pymodbus.client.sync import ModbusSerialClient


def get_ip_address(ifname):
    """
    Function to current device IP address based on interface name
    Args:
        ifname: string interface. e.g. eth0, wlan, etc

    Returns:
        string IP address
    """
    socket_instance = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        socket_instance.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', bytes(ifname[:15], 'utf-8'))
    )[20:24])


_LOGGER = logging.getLogger()


class ModBus(object):
    """
    Class ModBus has methods for sending and receiving ModBus commands over serial or TCP
    """

    __serial_client = None
    __device_file = None
    __tcp_client = None
    __is_serial = None

    def __init__(self, device_file="", timeout=5):
        """
        Initializes modbus communication

        Args:
            method: serial|tcp
            device_file: e.g. /dev/ttyUSB0
            host: e.g. 10.0.0.1
        """
        self.__is_serial = True
        self.__device_file = device_file
        self.__serial_client = ModbusSerialClient(method="rtu", port=device_file, baudrate=9600,
                                                  timeout=timeout)
        connection = self.__serial_client.connect()
        _LOGGER.info("ModBus:: Connection status with {} : {}"
                     .format(self.__device_file if self.__is_serial else self.__tcp_client,
                             connection))

    def close(self):
        """
        Closes connection
        """
        _LOGGER.info('ModBus::close:: Closing connection with {}'.format(
            self.__device_file if self.__is_serial else self.__tcp_client))
        self.__serial_client.close()

    def read_input_registers(self, address, count=2, unit=0x02):
        """
        Reads and returns modbus register.

        Args:
            address: Starting numerical modbus register address.
            count: Number of registers.
            unit: Slave address.

        Returns:
            Returns object(s).
        """
        return self.__serial_client.read_input_registers(address, count, unit=unit)

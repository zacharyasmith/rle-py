"""
components/Exceptions.py

Author:
    Zachary Smith
"""


class TimeoutException(Exception):
    """
    Exception intended for handling Timeouts.
    """
    def __init__(self, *args, **kwargs):
        """
        Args:
            args:
            kwargs:
        """
        Exception.__init__(self, *args, **kwargs)


class ConnectionRefusalException(Exception):
    """
    Exception intended for handling connection refusal errors.
    """
    def __init__(self, *args, **kwargs):
        """
        Args:
            args:
            kwargs:
        """
        Exception.__init__(self, *args, **kwargs)


class OperationsOutOfOrderException(Exception):
    """
    Exception intended for handling out of order operation issues.
    """
    def __init__(self, *args, **kwargs):
        """
        Args:
            args:
            kwargs:
        """
        Exception.__init__(self, *args, **kwargs)

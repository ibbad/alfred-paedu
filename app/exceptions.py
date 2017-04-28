"""
Custom exceptions for the application.
"""


class ValidationError(ValueError):
    pass


class TimeoutError(Exception):
    pass
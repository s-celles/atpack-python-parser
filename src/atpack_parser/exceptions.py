"""Custom exceptions for AtPack parser."""


class AtPackError(Exception):
    """Base exception for AtPack parsing errors."""

    pass


class DeviceNotFoundError(AtPackError):
    """Raised when a requested device is not found in the AtPack."""

    pass


class ParseError(AtPackError):
    """Raised when there's an error parsing AtPack files."""

    pass


class UnsupportedFormatError(AtPackError):
    """Raised when the AtPack format is not supported."""

    pass

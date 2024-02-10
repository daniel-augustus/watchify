class WatcherError(Exception):
    """Base project exceptions."""


class NotAnObserverError(WatcherError):
    """Placed object is not a valid observer."""


class PushError(WatcherError):
    """Observer has failed to process a push."""


class SpyError(WatcherError):
    """Spy attempt has failed."""

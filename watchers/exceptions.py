class WatcherError(Exception):
    """Base project exceptions."""


class NotAWatcherError(WatcherError):
    """Placed object is not a valid listener."""

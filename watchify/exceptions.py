class WatcherError(Exception):
    """Base project exceptions."""


class NotAnObserverError(WatcherError):
    """Placed object is not a valid observer."""


class NotAnOrchestratorError(WatcherError):
    """Placed object is not a valid observers manager."""


class PushError(WatcherError):
    """Observer has failed to process a push."""


class SpyError(WatcherError):
    """Spy related operations base error."""


class PoolError(WatcherError):
    """Requested action inside observers pool has failed."""

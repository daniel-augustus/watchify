class WatcherError(Exception):
    """Base project exceptions."""


class NotAWatcherError(WatcherError):
    """Placed object is not a valid listener."""


class PushError(WatcherError):
    """Listener has failed to process a push."""


class SpyError(WatcherError): pass

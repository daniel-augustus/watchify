import typing as t
from watchers.abstract import AbstractWatcher, AbstractWatchers


def is_watcher(obj: t.Any) -> bool:
    """Check if the provided instance is a valid `AbstractWatcher`."""
    return isinstance(obj, AbstractWatcher)

def is_watchers(obj: t.Any) -> bool:
    """Check if the provided instance is a valid `AbstractWatchers`."""
    return isinstance(obj, AbstractWatchers)

import typing as t
from watchers.interfaces import AbstractWatcher, AbstractWatchers


def is_watcher(obj: t.Any) -> bool:
    """Check if the provided instance is a valid `AbstractWatcher`.

    Parameters
    ----------
    obj: target be perform the `AbstractWatcher` checking.

    Examples
    ----------
    >>> is_watcher(CatWatcher())
    True
    >>> is_watcher(Watchers())
    False
    """
    return isinstance(obj, AbstractWatcher)


def is_watchers(obj: t.Any) -> bool:
    """Check if the provided instance is a valid `AbstractWatchers`.

    Parameters
    ----------
    obj: target be perform the `AbstractWatchers` checking.

    Examples
    ----------
    >>> is_watchers(Watchers())
    True
    >>> is_watchers(CatWatcher())
    False
    """
    return isinstance(obj, AbstractWatchers)

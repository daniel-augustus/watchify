import typing as t
from abc import ABC, abstractmethod


class AbstractWatcher:
    """Interface for minimum observers implementation."""

    def __repr__(self) -> str:
        return f'{self.__class__.__name__} object'

    @abstractmethod
    def push(self, sender: t.Any, *args, **kwargs) -> None:
        """`push` is called by observers manager to notify an event."""


class AbstractWatchers(ABC):
    """Interface for minimum observers manager implementation."""

    @abstractmethod
    def attach(self, watcher: AbstractWatcher) -> 'AbstractWatchers':
        """Add a watcher to the pool of observers."""

    @abstractmethod
    def attach_many(self, watchers: t.List[AbstractWatcher]) -> 'AbstractWatchers':
        """Add a list of watchers to the pool of observers."""

    @abstractmethod
    def detach(self, watcher: AbstractWatcher) -> 'AbstractWatchers':
        """Remove a watcher from the pool of observers."""

    @abstractmethod
    def detach_many(self, watchers: t.List[AbstractWatcher]) -> 'AbstractWatchers':
        """Remove a list of watchers from the pool of observers."""

    @abstractmethod
    def observers(self) -> t.List[AbstractWatcher]:
        """Bring observers pool."""

    @abstractmethod
    def notify(self, sender: t.Any, *args, **kwargs) -> 'AbstractWatchers':
        """Notify all observers."""


class AbstractSpyContainer(ABC):
    """Interface for minimum spy container implementation."""

    @abstractmethod
    def restore_state(self) -> None:
        """Restore instance to its prior spy state."""

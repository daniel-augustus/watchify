import typing as t
from abc import ABC, abstractmethod


class AbstractWatcher:
    """Interface for minimum listeners implementation."""

    def __repr__(self):
        return f'{self.__class__.__name__} object'

    @abstractmethod
    def push(self, sender: t.Any, *args, **kwargs) -> None:
        """`push` is called by listeners manager to notify an event."""


class AbstractWatchers(ABC):
    """Interface for minimum listeners manager implementation."""

    @abstractmethod
    def attach(self, watcher: AbstractWatcher) -> 'AbstractWatchers':
        """Add a watcher to the pool of listeners."""

    @abstractmethod
    def attach_many(self, watchers: t.List[AbstractWatcher]) -> 'AbstractWatchers':
        """Add a list of watchers to the pool of listeners."""

    @abstractmethod
    def detach(self, watcher: AbstractWatcher) -> 'AbstractWatchers':
        """Remove a watcher from the pool of listeners."""

    @abstractmethod
    def detach_many(self, watchers: t.List[AbstractWatcher]) -> 'AbstractWatchers':
        """Remove a list of watchers from the pool of listeners."""

    @abstractmethod
    def notify(self, sender: t.Any, *args, **kwargs) -> 'AbstractWatchers':
        """Notify all listeners."""

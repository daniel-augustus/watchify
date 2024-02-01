import logging
import typing as t
from copy import deepcopy
from typing import List
from watchers import functions
from watchers.abstract import AbstractWatcher, AbstractWatchers
from watchers.exceptions import NotAWatcherError, PushError
from watchers.logger import logger as internal_logger


class WatchersLite(AbstractWatchers):
    """Base implementation to schedule listeners and notify them."""

    def __init__(self):
        self._watchers: t.List[AbstractWatcher] = []

    def __iter__(self):
        for watcher in self._watchers:
            yield watcher

    def __add__(self, watchers: 'WatchersLite') -> 'WatchersLite':
        output_watchers = deepcopy(self)
        output_watchers.attach_many(watchers.listeners())
        return output_watchers

    def __call__(self, *args, **kwargs) -> None:
        self.notify(*args, **kwargs)

    def __getitem__(self, index: int) -> AbstractWatcher:
        try:
            return self._watchers[index]
        except IndexError:
            raise IndexError(f'Watchers has <{self.count()}> length.')

    def __repr__(self):
        watchers = ''
        for watcher in self._watchers[:8]:
            watchers += f'{watcher.__class__.__name__}, '
        watchers = watchers[:-2]
        if self.count() > 8:
            watchers += ', ...'
        return f'<Watchers object:Listeners[{watchers}]>'

    def count(self) -> int:
        """Bring the current listeners count."""
        return len(self._watchers)

    def reset(self) -> 'WatchersLite':
        """Prune all saved listeners."""
        self._watchers.clear()
        return self

    def listeners(self, as_type: t.Optional[t.Iterable] = None) -> t.Iterable[AbstractWatcher]:
        """Bring all listeners."""
        return self._watchers if not as_type else as_type(self._watchers)

    def attach(self, watcher: AbstractWatcher) -> 'WatchersLite':
        """Add a listener to watcher's pool to notify it about an event."""
        self._watchers.append(watcher)
        return self

    def attach_many(self, watchers: t.List[AbstractWatcher]) -> 'WatchersLite':
        """Add listeners to watcher's pool to notify them about an event."""
        self._watchers.extend(watchers)
        return self

    def detach(self, watcher: AbstractWatcher) -> 'WatchersLite':
        """Remove a listener from watcher's pool."""
        self._watchers.remove(watcher)
        return self

    def detach_many(self, watchers: t.List[AbstractWatcher]) -> 'WatchersLite':
        """Remove listeners from watcher's pool."""
        [self._watchers.remove(watcher) for watcher in watchers]
        return self

    def notify(self, sender: t.Any, *args, **kwargs) -> 'WatchersLite':
        """Notify all listeners about some change that may interest any of them."""
        [watcher.push(sender, *args, **kwargs) for watcher in self._watchers]


class Watchers(WatchersLite):

    def __init__(
        self,
        logger: t.Optional[logging.Logger] = None,
        disable_logs: bool = False,
        validate: bool = True,
    ):
        super().__init__()
        self._logger = logger or internal_logger
        self._logger.disabled = disable_logs
        self._validate = validate

    @staticmethod
    def _is_watcher(obj: t.Any):
        """Raise an exception if the provided object is not a valid listener."""
        if not functions.is_watcher(obj):
            raise NotAWatcherError(f"Expected <class 'AbstractWatcher'>, but got {type(obj)}.")

    @staticmethod
    def _is_watchers(obj: t.Any):
        """Raise an exception if the provided object is not a valid listener manager."""
        if not functions.is_watchers(obj):
            raise NotAWatcherError(f"Expected <class 'AbstractWatchers'>, but got {type(obj)}.")

    def __add__(self, watchers: 'Watchers') -> 'Watchers':
        self._is_watchers(watchers) if self._validate else None
        return super().__add__(watchers)

    def attach(self, watcher: AbstractWatcher) -> 'Watchers':
        self._is_watcher(watcher) if self._validate else None
        super().attach(watcher)
        self._logger.debug(f'Subscribed watcher: {watcher}.')
        return self

    def attach_many(self, watchers: List[AbstractWatcher]) -> 'Watchers':
        [self._is_watcher(watcher) for watcher in watchers] if self._validate else None
        super().attach_many(watchers)
        self._logger.debug(f'Subscribed watchers: {watchers}.')
        return self

    def detach(self, watcher: AbstractWatcher) -> 'Watchers':
        super().detach(watcher)
        self._logger.debug(f'Unsubscribed watcher: {watcher}.')

    def detach_many(self, watchers: List[AbstractWatcher]) -> 'Watchers':
        super().detach_many(watchers)
        self._logger.debug(f'Unsubscribed watchers: {watchers}.')

    def notify(
        self,
        sender: t.Any,
        *args,
        raise_exception: t.Optional[bool] = None,
        **kwargs,
    ) -> 'Watchers':
        for watcher in self._watchers:
            self._logger.debug(f'Notifying watcher: {watcher}.')
            try:
                watcher.push(sender, *args, **kwargs)
            except Exception as e:
                if raise_exception:
                    raise PushError(repr(e))
                else:
                    self._logger.error(f'Watcher: {watcher} failed to process an event. Exception: {repr(e)}.')

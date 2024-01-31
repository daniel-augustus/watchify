import typing as t
from copy import deepcopy
from watchers.abstract import AbstractWatcher, AbstractWatchers


class WatchersLite(AbstractWatchers):
    """Base implementation to schedule listeners and notify them."""

    def __init__(self):
        self._watchers: t.List[AbstractWatcher] = []

    def __iter__(self):
        for watcher in self._watchers:
            yield watcher

    def __add__(self, watchers: 'WatchersLite') -> 'WatchersLite':
        output_watchers = deepcopy(self)
        output_watchers.subscribe_n(watchers.listeners())
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

    def subscribe(self, watcher: AbstractWatcher) -> 'WatchersLite':
        """Add a listener to watcher's pool to notify it about an event."""
        self._watchers.append(watcher)
        return self

    def subscribe_n(self, watchers: t.List[AbstractWatcher]) -> 'WatchersLite':
        """Add listeners to watcher's pool to notify them about an event."""
        self._watchers.extend(watchers)
        return self

    def unsubscribe(self, watcher: AbstractWatcher) -> 'WatchersLite':
        """Remove a listener from watcher's pool."""
        self._watchers.remove(watcher)
        return self

    def unsubscribe_n(self, watchers: t.List[AbstractWatcher]) -> 'WatchersLite':
        """Remove listeners from watcher's pool."""
        [self._watchers.remove(watcher) for watcher in watchers]
        return self

    def notify(self, sender: t.Any, *args, **kwargs) -> 'WatchersLite':
        """Notify all listeners about some change that may interest any of them."""
        [watcher.push(sender, *args, **kwargs) for watcher in self._watchers]

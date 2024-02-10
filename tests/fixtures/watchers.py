import pytest
import typing as t
from watchify.interfaces import AbstractWatcher
from watchify.watchers import Watchers, WatchersLite


@pytest.fixture
def watchers() -> WatchersLite:
    """Create a `Watchers` object."""
    return Watchers()


@pytest.fixture
def watchers_lite() -> WatchersLite:
    """Create a `WatchersLite` object."""
    return WatchersLite()


@pytest.fixture
def cat_watcher() -> AbstractWatcher:
    """Create an `AbstractWatcher` specialization using kitty metaphor."""
    class CatWatcher(AbstractWatcher):
        def push(self, sender: t.Any, *args, **kwargs):
            if sender.name == 'fish':
                return f'Cat loves {sender.name}!'
            else:
                return f'Cat hates {sender.name}!'

    return CatWatcher()


@pytest.fixture
def monkey_watcher() -> AbstractWatcher:
    """Create an `AbstractWatcher` specialization using kitty metaphor."""
    class MonkeyWatcher(AbstractWatcher):
        def push(self, sender: t.Any, *args, **kwargs):
            if sender.name == 'banana':
                return f'Monkey loves {sender.name}!'
            else:
                return f'Monkey hates {sender.name}!'

    return MonkeyWatcher()

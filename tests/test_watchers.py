from copy import deepcopy
from pytest_mock import MockerFixture
from watchers.abstract import AbstractWatcher
from watchers.watchers import WatchersLite


class TestWatchersLite:
    """Tests for `watchers.watcher.WatchersLite` implementation."""

    def test_init(self):
        """Validations on `__init__` method."""
        watchers_lite = WatchersLite()
        assert getattr(watchers_lite, '_watchers') == []

    def test_add(
        self,
        cat_watcher: AbstractWatcher,
        monkey_watcher: AbstractWatcher,
        watchers_lite: WatchersLite,
    ):
        """Validations on `__add__` method."""
        watchers_lite_copy = deepcopy(watchers_lite)
        watchers_lite_copy.attach(monkey_watcher)
        watchers_lite.attach(cat_watcher)
        watchers = watchers_lite + watchers_lite_copy
        assert watchers_lite.count() == 1
        assert watchers_lite_copy.count() == 1
        assert watchers.count() == 2

    def test_contains(
        self,
        cat_watcher: AbstractWatcher,
        monkey_watcher: AbstractWatcher,
        watchers_lite: WatchersLite,
    ):
        """Validations on `__contains__` method."""
        watchers = [cat_watcher, monkey_watcher]
        watchers_lite.attach_many(watchers)
        for watcher in watchers:
            assert watcher in watchers_lite

    def test_iter(
        self,
        cat_watcher: AbstractWatcher,
        monkey_watcher: AbstractWatcher,
        watchers_lite: WatchersLite,
    ):
        """Validations on `__iter__` method."""
        watchers = [cat_watcher, monkey_watcher]
        watchers_lite.attach_many(watchers)
        for index, watcher in enumerate(watchers_lite):
            assert watcher == watchers[index]

    def test_getitem(
        self,
        cat_watcher: AbstractWatcher,
        monkey_watcher: AbstractWatcher,
        watchers_lite: WatchersLite,
    ):
        """Validations on `__getitem__` method."""
        watchers_lite.attach_many([cat_watcher, monkey_watcher])
        assert watchers_lite[0] == cat_watcher
        assert watchers_lite[1] == monkey_watcher

    def test_repr(self, cat_watcher: AbstractWatcher, watchers_lite: WatchersLite):
        """Validations on `__repr__` method."""
        watchers_lite.attach(cat_watcher)
        assert watchers_lite.__repr__() == '<WatchersLite object:Observers[CatWatcher]>'

    def test_repr_truncated(self, cat_watcher: AbstractWatcher, watchers_lite: WatchersLite):
        """Validations on `__repr__` method with truncated observers sequence."""
        watchers_lite.attach_many([cat_watcher] * 20)
        assert watchers_lite.__repr__() == (
            '<WatchersLite object:Observers[CatWatcher, CatWatcher, CatWatcher, CatWatcher, '
            'CatWatcher, CatWatcher, CatWatcher, CatWatcher, ...]>'
        )

    def test_count(self, cat_watcher: AbstractWatcher, watchers_lite: WatchersLite):
        """Validations on `count` method."""
        assert watchers_lite.count() == 0
        watchers_lite.attach(cat_watcher)
        assert watchers_lite.count() == 1

    def test_reset(self, cat_watcher: AbstractWatcher, watchers_lite: WatchersLite):
        """Validations on `reset` method."""
        watchers_lite.attach(cat_watcher)
        assert cat_watcher in watchers_lite
        watchers_lite.reset()
        assert cat_watcher not in watchers_lite

    def test_observers(self, cat_watcher: AbstractWatcher, watchers_lite: WatchersLite):
        """Validations on `observers` method."""
        assert watchers_lite.observers() == []
        watchers_lite.attach(cat_watcher)
        assert watchers_lite.observers() == [cat_watcher]

    def test_attach(self, cat_watcher: AbstractWatcher, watchers_lite: WatchersLite):
        """Validations on `attach` method."""
        assert cat_watcher in watchers_lite.attach(cat_watcher)

    def test_attach_many(
        self,
        cat_watcher: AbstractWatcher,
        monkey_watcher: AbstractWatcher,
        watchers_lite: WatchersLite,
    ):
        """Validations on `attach_many` method."""
        watchers = [cat_watcher, monkey_watcher]
        assert all(watcher in watchers_lite.attach_many(watchers) for watcher in watchers)

    def test_detach(self, cat_watcher: AbstractWatcher, watchers_lite: WatchersLite):
        """Validations on `detach` method."""
        assert cat_watcher not in watchers_lite.attach(cat_watcher).detach(cat_watcher)

    def test_detach_many(
        self,
        cat_watcher: AbstractWatcher,
        monkey_watcher: AbstractWatcher,
        watchers_lite: WatchersLite,
    ):
        """Validations on `detach_many` method."""
        watchers = [cat_watcher, monkey_watcher]
        assert all(
            watcher not in watchers_lite.attach_many(watchers).detach_many(watchers)
            for watcher in watchers
        )

    def test_notify(
        self,
        mocker: MockerFixture,
        cat_watcher: AbstractWatcher,
        food_sender: object,
        watchers_lite: WatchersLite
    ):
        """Validations on `notify` method."""
        watchers_lite.attach(cat_watcher)
        mock_push = mocker.patch.object(cat_watcher, 'push')
        food_sender.cook('fish')
        watchers_lite.notify(food_sender)
        mock_push.assert_called_once()

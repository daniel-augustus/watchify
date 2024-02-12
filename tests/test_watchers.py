import pytest
from copy import deepcopy
from pytest_mock import MockerFixture
from watchify import exceptions as e
from watchify.interfaces import AbstractWatcher
from watchify.watchers import Watchers, WatchersLite


class TestWatchersLite:
    """Tests for `watchify.watcher.WatchersLite` implementation."""

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

    def test_call(self, watchers_lite: WatchersLite, mocker: MockerFixture):
        """Validations on `__call__` method."""
        mock_notify = mocker.patch.object(watchers_lite, 'notify')
        watchers_lite()
        mock_notify.assert_called_once()

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


class TestWatchers:
    """Tests for `watchify.watcher.Watchers` implementation."""

    @pytest.fixture
    def dummy_watcher(self) -> AbstractWatcher:
        """Dummy `AbstractWatcher` for testing purposes."""
        class DummyWatcher(AbstractWatcher):
            def push(self, *args, **kwargs):
                raise Exception

        return DummyWatcher()

    def test_add(self, watchers: Watchers):
        """Validations on `__add__` method."""
        output_watchers = watchers + Watchers()
        assert isinstance(output_watchers, Watchers)

    def test_add_exception(self, watchers: Watchers):
        """Validations on `__add__` method when an incorrect instance is provided."""
        with pytest.raises(e.NotAnOrchestratorError):
            watchers + 1

    def test_getitem(self, watchers: Watchers, cat_watcher: AbstractWatcher):
        """Validations on `__getitem__` method."""
        observer = watchers.attach(cat_watcher)[0]
        assert isinstance(observer, AbstractWatcher)

    def test_getitem_exception(self, watchers: Watchers, cat_watcher: AbstractWatcher):
        """Validations on `__getitem__` method when an incorrect index is provided."""
        with pytest.raises(e.WatcherError):
            watchers.attach(cat_watcher)[1]

    def test_repr(self, watchers: Watchers, cat_watcher: AbstractWatcher):
        """Validations on `__repr__` method."""
        watchers.attach(cat_watcher)
        assert watchers.__repr__() == '<Watchers object:Observers[CatWatcher]>'

    def test_is_watcher(self, watchers: Watchers, cat_watcher: AbstractWatcher):
        """Validations on `is_watcher` method."""
        assert watchers._is_watcher(cat_watcher) is None

    def test_is_watcher_exception(self, watchers: Watchers):
        """Validations on `is_watcher` method when an invalid object is provided."""
        with pytest.raises(e.NotAnObserverError):
            watchers._is_watcher(1)

    def test_is_watchers(self, watchers: Watchers):
        """Validations on `is_watchers` method."""
        assert watchers._is_watchers(watchers) is None

    def test_is_watchers_exception(self, watchers: Watchers, cat_watcher: AbstractWatcher):
        """Validations on `is_watchers` method when an invalid object is provided."""
        with pytest.raises(e.NotAnOrchestratorError):
            watchers._is_watchers(cat_watcher)

    def test_attach(self, watchers: Watchers, cat_watcher: AbstractWatcher):
        """Validations on `attach` method."""
        watchers.attach(cat_watcher)
        assert watchers.count() == 1

    def test_attach_exception(self, watchers: Watchers):
        """Validations on `attach` method when an invalid object is provided."""
        with pytest.raises(e.NotAnObserverError):
            watchers.attach(1)

    def test_attach_many(
        self,
        watchers: Watchers,
        cat_watcher: AbstractWatcher,
        monkey_watcher: AbstractWatcher,
    ):
        """Validations on `attach_many` method."""
        watchers.attach_many([cat_watcher, monkey_watcher])
        assert watchers.count() == 2

    def test_attach_many_exception(self, watchers: Watchers, cat_watcher: AbstractWatcher):
        """Validations on `attach_many` method when an invalid object is provided."""
        with pytest.raises(e.NotAnObserverError):
            watchers.attach_many([cat_watcher, 1])

    def test_detach(self, watchers: Watchers, cat_watcher: AbstractWatcher):
        """Validations on `detach` method."""
        watchers.attach(cat_watcher)
        watchers.detach(cat_watcher)
        assert watchers.count() == 0

    def test_detach_exception(self, watchers: Watchers):
        """Validations on `detach` method when an object is not found inside pool."""
        with pytest.raises(e.WatcherError):
            watchers.detach(1)

    def test_detach_many(
        self,
        watchers: Watchers,
        cat_watcher: AbstractWatcher,
        monkey_watcher: AbstractWatcher,
    ):
        """Validations on `detach_many` method."""
        watchers.attach_many([cat_watcher, monkey_watcher])
        watchers.detach_many([cat_watcher, monkey_watcher])
        watchers.count() == 0

    def test_detach_many_exception(self, watchers: Watchers, cat_watcher: AbstractWatcher):
        """Validations on `detach_many` method when an invalid object is provided."""
        with pytest.raises(e.WatcherError):
            watchers.detach_many([cat_watcher, 1])

    def test_notify(
        self,
        mocker: MockerFixture,
        watchers: Watchers,
        cat_watcher: AbstractWatcher,
        dummy_watcher: AbstractWatcher,
        food_sender: object,
    ):
        """Validations on `notify` method."""
        watchers.attach_many([cat_watcher, dummy_watcher])
        mock_push = mocker.patch.object(cat_watcher, 'push')
        food_sender.cook('fish')
        watchers.notify(food_sender)
        mock_push.assert_called_once()

    def test_notify_exception(
        self,
        watchers: Watchers,
        cat_watcher: AbstractWatcher,
        dummy_watcher: AbstractWatcher,
        food_sender: object,
    ):
        """Validations on `notify` method if `raises_exception=True` is provided."""
        watchers.attach_many([cat_watcher, dummy_watcher])
        food_sender.cook('fish')
        with pytest.raises(Exception):
            watchers.notify(food_sender, raise_exception=True)

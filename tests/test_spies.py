import pytest
from pytest_mock import MockerFixture
from watchify.exceptions import SpyError
from watchify.interfaces import AbstractWatcher
from watchify.spies import AbstractSpyContainer, WatchersSpy


class TestWatchersSpy:
    """Tests for `watchify.spies.WatchersSpy` implementation."""

    @pytest.fixture
    def dummy(self) -> object:
        """Dummy object for testing purposes."""
        class Dummy:
            def main(self) -> None:
                pass

        return Dummy()

    def test_repr(self, cat_watcher: AbstractWatcher, watchers_spy: WatchersSpy):
        """Validations on `__repr__` method."""
        watchers_spy.attach(cat_watcher)
        assert watchers_spy.__repr__() == '<WatchersSpy object:Observers[CatWatcher]>'

    def test_reset(self, cat_watcher: AbstractWatcher, watchers_spy: WatchersSpy, dummy: object):
        """Validations on `reset` method."""
        assert not watchers_spy.spies()
        assert not watchers_spy.observers()
        watchers_spy.spy(dummy, 'main')
        watchers_spy.attach(cat_watcher)
        assert watchers_spy.spies()
        assert watchers_spy.observers()
        watchers_spy.reset()
        assert not watchers_spy.spies()
        assert not watchers_spy.observers()

    def test_partial_reset(
        self,
        dummy: object,
        cat_watcher: AbstractWatcher,
        watchers_spy: WatchersSpy,
    ):
        """Validations on `reset` method when `reset_spies=False` is requested."""
        watchers_spy.spy(dummy, 'main')
        watchers_spy.attach(cat_watcher)
        watchers_spy.reset(reset_spies=False)
        assert watchers_spy.spies()
        assert not watchers_spy.observers()

    def test_spy(self, watchers_spy: WatchersSpy, dummy: object, mocker: MockerFixture):
        """Validations on `spy` method."""
        spy_notify = mocker.spy(watchers_spy, 'notify')
        watchers_spy.spy(dummy, 'main')
        dummy.main()
        spy_notify.assert_called_once()

    def test_spy_invalid_spy(self, watchers_spy: WatchersSpy, dummy: object):
        """Validations on `spy` method when an invalid `trigger` arg is provided."""
        with pytest.raises(SpyError):
            watchers_spy.spy(dummy, 'main', 'unkown')

    def test_spies(self, watchers_spy: WatchersSpy, dummy: object):
        """Validations on `spies` method."""
        assert len(watchers_spy.spies()) == 0
        watchers_spy.spy(dummy, 'main')
        spies = watchers_spy.spies()
        assert len(spies) == 1
        assert isinstance(spies[0], AbstractSpyContainer)

    def test_undo_spy(self, watchers_spy: WatchersSpy, dummy: object, mocker: MockerFixture):
        """Validations on `undo_spy` method."""
        spy_notify = mocker.spy(watchers_spy, 'notify')
        watchers_spy.spy(dummy, 'main')
        dummy.main()
        spy_notify.assert_called_once()
        watchers_spy.undo_spy(dummy, 'main')
        assert not watchers_spy.spies()
        spy_notify.reset_mock()
        dummy.main()
        spy_notify.assert_not_called()

    def test_undo_spies(self, watchers_spy: WatchersSpy, dummy: object):
        """Validations on `undo_spies` method."""
        class AnotherDummy:
            def main(self) -> None:
                pass

        watchers_spy.spy(dummy, 'main')
        watchers_spy.spy(AnotherDummy(), 'main')
        assert len(watchers_spy.spies()) == 2
        watchers_spy.undo_spies()
        assert len(watchers_spy.spies()) == 0

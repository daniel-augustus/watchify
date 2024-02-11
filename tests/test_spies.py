import pytest
from pytest_mock import MockerFixture
from watchify.exceptions import SpyError
from watchify.interfaces import AbstractWatcher
from watchify.spies import AbstractSpyContainer, SpyContainer, WatchersSpy


@pytest.fixture
def dummy() -> object:
    """Dummy object for testing purposes."""
    class Dummy:

        def __repr__(self) -> str:
            return 'Dummy object'

        def main(self) -> None:
            return None

    return Dummy()


class TestSpyContainer:
    """Tests for `watchify.spies.SpyContainer` implementation."""

    def test_repr(self, dummy: object):
        """Validations on `__repr__` method."""
        container = SpyContainer(dummy, 'main', constraint='after', original_state=None)
        assert repr(container) == "Spying(sender='Dummy object', method='main', constraint='after')"

    def test_repr_truncated(self, dummy: object):
        """Validations on `__repr__` method for too long constraints."""
        constraint = str([1] * 81)
        container = SpyContainer(dummy, 'main', constraint=constraint, original_state=None)
        assert repr(container) == (
            f"Spying(sender='Dummy object', method='main', constraint='{constraint[:80]}...')"
        )


class TestWatchersSpy:
    """Tests for `watchify.spies.WatchersSpy` implementation."""

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

    def test_spy_after(self, watchers_spy: WatchersSpy, dummy: object, mocker: MockerFixture):
        """Validations on `spy_after` flow."""
        mock_main = mocker.patch.object(dummy, 'main')
        mock_notify = mocker.patch.object(watchers_spy, 'notify')
        watchers_spy._spy(dummy, 'main', getattr(dummy, 'main'), trigger='after')
        dummy.main()
        mock_main.assert_called_once()
        mock_notify.assert_called_once()

    def test_spy_before(self, watchers_spy: WatchersSpy, dummy: object, mocker: MockerFixture):
        """Validations on `spy_before` flow."""
        mock_main = mocker.patch.object(dummy, 'main')
        mock_notify = mocker.patch.object(watchers_spy, 'notify')
        watchers_spy._spy(dummy, 'main', getattr(dummy, 'main'), trigger='before')
        dummy.main()
        mock_main.assert_called_once()
        mock_notify.assert_called_once()

    def test_spy_on_return(self, watchers_spy: WatchersSpy, dummy: object, mocker: MockerFixture):
        """Validations on `spy_on_return` flow."""
        mock_main = mocker.patch.object(dummy, 'main')
        mock_main.return_value = None
        mock_notify = mocker.patch.object(watchers_spy, 'notify')
        watchers_spy._spy(dummy, 'main', getattr(dummy, 'main'), on_return=(None,))
        dummy.main()
        mock_main.assert_called_once()
        mock_notify.assert_called_once()

    def test_spy_on_return_skip(
        self,
        dummy: object,
        mocker: MockerFixture,
        watchers_spy: WatchersSpy,
    ):
        """Validations on `spy_on_return` flow skipping `notify` call.."""
        mock_main = mocker.patch.object(dummy, 'main')
        mock_main.return_value = ''
        mock_notify = mocker.patch.object(watchers_spy, 'notify')
        watchers_spy._spy(dummy, 'main', getattr(dummy, 'main'), on_return=(None,))
        dummy.main()
        mock_main.assert_called_once()
        mock_notify.assert_not_called()

    def test_spy_invalid_spy(self, watchers_spy: WatchersSpy, dummy: object):
        """Validations on `spy` method when an invalid `trigger` arg is provided."""
        with pytest.raises(SpyError):
            watchers_spy.spy(dummy, 'main', 'unkown')

    def test_attach(self, watchers_spy: WatchersSpy, cat_watcher: AbstractWatcher):
        """Validations on `attach` method."""
        assert not watchers_spy.observers()
        watchers_spy.attach(cat_watcher)
        assert watchers_spy.observers()
        assert isinstance(watchers_spy, WatchersSpy)

    def test_attach_many(self, watchers_spy: WatchersSpy, cat_watcher: AbstractWatcher):
        """Validations on `attach_many` method."""
        assert not watchers_spy.observers()
        watchers_spy.attach_many([cat_watcher])
        assert watchers_spy.observers()
        assert isinstance(watchers_spy, WatchersSpy)

    def test_detach(self, watchers_spy: WatchersSpy, cat_watcher: AbstractWatcher):
        """Validations on `detach` method."""
        assert not watchers_spy.observers()
        watchers_spy.attach(cat_watcher)
        assert watchers_spy.observers()
        watchers_spy.detach(cat_watcher)
        assert not watchers_spy.observers()
        assert isinstance(watchers_spy, WatchersSpy)

    def test_detach_many(self, watchers_spy: WatchersSpy, cat_watcher: AbstractWatcher):
        """Validations on `detach_many` method."""
        assert not watchers_spy.observers()
        watchers_spy.attach(cat_watcher)
        assert watchers_spy.observers()
        watchers_spy.detach_many([cat_watcher])
        assert not watchers_spy.observers()
        assert isinstance(watchers_spy, WatchersSpy)

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

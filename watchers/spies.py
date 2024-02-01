import typing as t
from watchers.watchers import Watchers, WatchersLite
from watchers.exceptions import SpyError


class SpyContainer:
    """Holds metadata from the spy process."""

    def __init__(
        self,
        sender: t.Any,
        target: str,
        trigger: str,
        original_state: t.Callable,
    ):
        self._sender = sender
        self._target = target
        self._trigger = trigger
        self._original_state = original_state

    def restore_state(self) -> None:
        """Undo the `WatchersSpy.spy` wrap from the sender."""
        setattr(self._sender, self._target, self._original_state)

    def __repr__(self):
        return f"Spying(sender={self._sender}, method={self._target}, trigger={self._trigger})"


class WatchersSpy(Watchers):


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._spies: t.Dict[t.Tuple[t.Type, str], SpyContainer] = {}

    def __repr__(self) -> str:
        """Show canonical representation, including dynamic truncated observers sequence.

        Examples
        --------
        >>> watchers = WatchersSpy().attach_many([CatWatcher(), MonkeyWatcher()])
        >>> watchers
        <WatchersSpy object:Observers[CatWatcher, MonkeyWatcher]>
        """
        instance = super().__repr__()
        return instance.replace('Watchers', 'WatchersSpy')

    def reset(self, reset_spies: bool = True) -> WatchersLite:
        """Prune all saved observers and spies.

        Parameters
        ----------
        reset_spies: calls `undo_spies` along with `reset` (*Default: `True`).

        Examples
        --------
        >>> watchers = WatchersSpy().attach_many([CatWatcher(), MonkeyWatcher()])
        >>> watchers
        <WatchersSpy object:Observers[CatWatcher, MonkeyWatcher]>
        >>> watchers.reset()
        >>> watchers
        <Watchers object:Observers[]>
        >>> watchers.spies()
        []
        """
        if reset_spies:
            self.undo_spies()
        return super().reset()

    def spy(self, sender: t.Union[t.Type[object], object], target: str, trigger: str = 'after') -> SpyContainer:
        """Imbue `notify` call to sender's callable."""
        if trigger not in ('before', 'after'):
            raise SpyError(f"Trigger '{trigger}' is not supported. Options are ('before', 'after')")
        method = getattr(sender, target)
        def spy_wrapper(*args, **kwargs):
            if trigger == 'after':
                method(*args, **kwargs)
                self.notify(*args, **kwargs)
            else:
                self.notify(*args, **kwargs)
                method(*args, **kwargs)
        setattr(sender, target, spy_wrapper)
        spy = SpyContainer(sender, target, trigger, method)
        self._spies[(sender, target)] = spy
        self._logger.debug(f"<sender '{sender}'> <method '{target}'> is now being spied...")
        return spy

    def spies(self, as_type: t.Optional[t.Iterable] = None) -> t.List[SpyContainer]:
        """

        """
        return list(self._spies.values()) if as_type is None else as_type(self._spies.values())

    def undo_spy(self, sender: t.Type, target: str) -> SpyContainer:
        spy = self._spies.pop((sender, target))
        spy.restore_state()
        self._logger.debug(f"<sender '{sender}'> <method '{target}'> is no longer being spied.")
        return spy

    def undo_spies(self) -> t.List[SpyContainer]:
        return [self.undo_spy(sender, target) for sender, target in tuple(self._spies.keys())]

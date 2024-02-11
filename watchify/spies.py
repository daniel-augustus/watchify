import typing as t
from functools import wraps
from watchify.exceptions import SpyError
from watchify.interfaces import AbstractSpyContainer, AbstractWatcher
from watchify.watchers import Watchers


class SpyContainer(AbstractSpyContainer):
    """Holds metadata from the spy process.

    Auxiliary `WatchersSpy` implementation functionalities.

    Parameters
    ----------
    sender : object being spied.
    target : object's callable name imbued with `Watchers.notify` functionality.
    constraint : `notify`'s orientation (`after`, `before`).
    original_state : object's callable state pior to spy process.
    """

    def __init__(
        self,
        sender: t.Any,
        target: str,
        constraint: str,
        original_state: t.Callable,
    ) -> None:
        """Save spied object information."""
        constraint = str(constraint)
        self._sender = sender
        self._target = target
        self._constraint = str(constraint)
        self._original_state = original_state

    def restore_state(self) -> None:
        """Undo the `WatchersSpy.spy` wrap from the sender."""
        setattr(self._sender, self._target, self._original_state)

    def __repr__(self) -> str:
        """Display instance being spied, its wrapped callable and the `nofify`'s orientation."""
        constraint, constraint_len = self._constraint, len(self._constraint)
        if constraint_len > 80:
            constraint = f'{constraint[:80]}...'
        return (
            f"Spying(sender='{self._sender}', method='{self._target}', constraint="
            f"'{constraint}')"
        )


class WatchersSpy(Watchers):
    """`Watchers` allowing imbuing objects with `notify` without changing them directly.

    Examples
    --------
    >>> class Food:
    ...    def cook(self, name: str):
    ...        self.name = name
    ...
    >>> class CatWatcher(AbstractWatcher):
    ...    def push(self, food: Food, *args, **kwargs):
    ...        if food.name == 'fish':
    ...            logger.debug(f'Cat loves %s!', food.name)
    ...        else:
    ...            logger.debug(f'Cat hates %s!', food.name)
    ...
    >>> class MonkeyWatcher(AbstractWatcher):
    ...    def push(self, food: Food, *args, **kwargs):
    ...        if food.name == 'banana':
    ...            logger.debug(f'Monkey loves %s!', food.name)
    ...        else:
    ...            logger.debug(f'Monkey hates %s!', food.name)
    ...
    >>> food, watchers = Food(), WatchersSpy()
    >>> watchers.attach_many([CatWatcher(), MonkeyWatcher()])
    <WatchersSpy object:Observers[CatWatcher, MonkeyWatcher]>
    >>> watchers.spy(food, 'cook')
    Spying(sender'=<Food object>', method='cook', constraint='after')
    >>> food.cook('fish')
    [watchers][DEBUG][2077-12-27 00:00:00,111] >>> Notifying watcher: CatWatcher object...
    [watchers][DEBUG][2077-12-27 00:00:00,112] >>> Cat loves fish!
    [watchers][DEBUG][2077-12-27 00:00:00,113] >>> Notifying watcher: MonkeyWatcher object...
    [watchers][DEBUG][2077-12-27 00:00:00,114] >>> Monkey hates fish!
    >>> food.cook('banana')
    [watchers][DEBUG][2077-12-27 00:00:00,115] >>> Notifying watcher: CatWatcher object...
    [watchers][DEBUG][2077-12-27 00:00:00,116] >>> Cat hates banana!
    [watchers][DEBUG][2077-12-27 00:00:00,117] >>> Notifying watcher: MonkeyWatcher object...
    [watchers][DEBUG][2077-12-27 00:00:00,118] >>> Monkey loves banana!
    """

    def __init__(self, *args, **kwargs) -> None:
        """`Watchers.__init__` along with an empty structure to track spies."""
        super().__init__(*args, **kwargs)
        self._spies: t.Dict[t.Tuple[t.Type, str], AbstractSpyContainer] = {}
        self._container = kwargs.pop('container', SpyContainer)

    def __repr__(self) -> str:
        """Show canonical representation, including dynamic truncated observers sequence.

        Examples
        --------
        >>> watchers = WatchersSpy().attach_many([CatWatcher(), MonkeyWatcher()])
        >>> watchers
        <WatchersSpy object:Observers[CatWatcher, MonkeyWatcher]>
        """
        return super().__repr__().replace('Watchers', 'WatchersSpy')

    def _spy_after(self, sender: t.Any, method: t.Callable[..., t.Any], *args, **kwargs) -> None:
        """Imbue a callable with `notify` call after it being invoked."""
        method(*args, **kwargs)
        self.notify(sender, *args, **kwargs)

    def _spy_before(self, sender: t.Any, method: t.Callable[..., t.Any], *args, **kwargs) -> None:
        """Imbue a callable with `notify` call before it being invoked."""
        self.notify(sender, *args, **kwargs)
        method(*args, **kwargs)

    def _spy_on_return(
        self,
        sender: t.Any,
        method: t.Callable[..., t.Any],
        on_return: t.Tuple[t.Any, ...],
        *args,
        **kwargs,
    ) -> None:
        """Imbue a callable with `notify` call if a condition is met."""
        output = method(*args, **kwargs)
        if output in on_return:
            self.notify(sender, *args, **kwargs)

    def _spy(
        self,
        sender: t.Union[t.Type[object], object],
        target: str,
        method: t.Callable[..., t.Any],
        trigger: str = 'after',
        on_return: t.Optional[t.Tuple[t.Any, ...]] = None,
    ) -> None:
        """Imbue a callable with `notify` call."""
        @wraps(method)
        def spy_wrapper(*args, **kwargs):
            if on_return:
                self._spy_on_return(sender, method, on_return, *args, **kwargs)
            elif trigger == 'after':
                self._spy_after(sender, method, *args, **kwargs)
            else:
                self._spy_before(sender, method, *args, **kwargs)
        setattr(sender, target, spy_wrapper)

    def spy(
        self,
        sender: t.Union[t.Type[object], object],
        target: str,
        trigger: str = 'after',
        on_return: t.Optional[t.Tuple[t.Any, ...]] = None,
    ) -> SpyContainer:
        """Imbue a callable with `notify` call without directly changing it.

        Parameters
        ----------
        sender : a class or instance to spy on.
        target : a method name to spy on.
        trigger : a trigger to call the `notify` method. Options are (`before`, `after`):
            * 'before' will call `notify` before the original method.
            * 'after' will call `notify` after the original method.
            * Default: 'after'.\n
        on_return : conditional `notify` trigger (has higher priority over `trigger` arg).

        Examples
        --------
        >>> class Food:
        ...     def cook(self, name: str):
        ...         self.name = name
        ...
        >>> food, watchers = Food(), WatchersSpy()
        >>> watchers.attach_many([CatWatcher(), MonkeyWatcher()])
        <WatchersSpy object:Observers[CatWatcher, MonkeyWatcher]>
        >>> watchers.spy(food, 'cook')
        Spying(sender'=<Food object>', method='cook', constraint='after')
        >>> food.cook('fish')
        [watchers][DEBUG][2077-12-27 00:00:00,111] >>> Notifying watcher: CatWatcher object...
        [watchers][DEBUG][2077-12-27 00:00:00,112] >>> Cat loves fish!
        [watchers][DEBUG][2077-12-27 00:00:00,113] >>> Notifying watcher: MonkeyWatcher object...
        [watchers][DEBUG][2077-12-27 00:00:00,114] >>> Monkey hates fish!
        """
        if not on_return and trigger not in ('before', 'after'):
            raise SpyError(f"Trigger '{trigger}' is not supported. Options are ('before', 'after')")
        method = getattr(sender, target)
        self._spy(sender, target, method, trigger, on_return)
        spy = self._container(sender, target, on_return or trigger, method)
        self._spies[(sender, target)] = spy
        self._logger.debug(f"<sender '{sender}'> <method '{target}'> is now being spied...")
        return spy

    def attach(self, watcher: AbstractWatcher) -> 'WatchersSpy':
        return super().attach(watcher)

    def attach_many(self, watchers: t.List[AbstractWatcher]) -> 'WatchersSpy':
        return super().attach_many(watchers)

    def detach(self, watcher: AbstractWatcher) -> 'WatchersSpy':
        return super().detach(watcher)

    def detach_many(self, watchers: t.List[AbstractWatcher]) -> 'WatchersSpy':
        return super().detach_many(watchers)

    def reset(self, reset_spies: bool = True) -> 'WatchersSpy':
        """Prune all saved observers and spies.

        Parameters
        ----------
        reset_spies : also triggers `undo_spies` along with `reset` (*Default: `True`).

        Examples
        --------
        >>> watchers = WatchersSpy().attach_many([CatWatcher(), MonkeyWatcher()])
        >>> watchers
        <WatchersSpy object:Observers[CatWatcher, MonkeyWatcher]>
        >>> watchers.reset()
        >>> watchers
        <WatchersSpy object:Observers[]>
        >>> watchers.spies()
        []
        """
        if reset_spies:
            self.undo_spies()
        return super().reset()

    def spies(
        self,
        as_type: t.Optional[t.Callable[[t.Iterable], t.Iterable]] = None,
    ) -> t.Iterable[AbstractSpyContainer]:
        """Bring all spied objects.

        Parameters
        ----------
        as_type : optional cast to be applied on spied objects (*Defaut: `None`).

        Examples
        --------
        >>> class Food:
        ...     def cook(self, name: str): ...
        ...
        >>> watchers = WatchersSpy()
        >>> watchers.spy(food(), 'cook')
        >>> watchers.spies()
        [Spying(sender'=<Food object>', method='cook', constraint='after')]
        >>> watchers.spies(set)
        {Spying(sender'=<Food object>', method='cook', constraint='after')}
        """
        return list(self._spies.values()) if as_type is None else as_type(self._spies.values())

    def undo_spy(self, sender: t.Any, target: str) -> SpyContainer:
        """Stop spying an object by removing the `notify` wrapper applied by `spy` method.

        Parameters
        ----------
        sender : event source.
        target : sender's callable to be wrapped.

        Examples
        --------
        >>> class Food:
        ...     def cook(self, name: str): ...
        ...
        >>> food, watchers = Food(), WatchersSpy()
        >>> watchers.spy(food, 'cook')
        Spying(sender'=<Food object>', method='cook', constraint='after')
        >>> watchers.undo_spy(food, 'cook')
        Spying(sender'=<Food object>', method='cook', constraint='after')
        """
        spy = self._spies.pop((sender, target))
        spy.restore_state()
        self._logger.debug(f"<sender '{sender}'> <method '{target}'> is no longer being spied.")
        return spy

    def undo_spies(self) -> t.List[AbstractSpyContainer]:
        """Run `undo_spy` on all stored spied objects.

        Examples
        --------
        >>> class Food:
        ...     def cook(self, name: str): ...
        ...
        >>> food_a, food_b, watchers = Food(), Food(),  WatchersSpy()
        >>> watchers.spy(food_a, 'cook', 'after')
        Spying(sender'=<Food object>', method='cook', constraint='after')
        >>> watchers.spy(food_b, 'cook', 'before')
        Spying(sender'=<Food object>', method='cook', constraint='before')
        >>> watchers.undo_spies()
        [
            Spying(sender'=<Food object>', method='cook', constraint='after'),
            Spying(sender'=<Food object>', method='cook', constraint='before'),
        ]
        """
        return [self.undo_spy(sender, target) for sender, target in tuple(self._spies.keys())]

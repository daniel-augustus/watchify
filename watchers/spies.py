import typing as t
from watchers.abstract import AbstractSpyContainer
from watchers.watchers import Watchers, WatchersLite
from watchers.exceptions import SpyError


class SpyContainer(AbstractSpyContainer):
    """Holds metadata from the spy process.

    Auxiliary code for `WatchersSpy` functionalities.

    Parameters
    ----------
    sender : object being spied.
    target : object's callable name imbued with `Watchers.notify` functionality.
    trigger : `notify`'s orientation (`after`, `before`).
    original_state : object's callable state pior to spy process.
    """

    def __init__(
        self,
        sender: t.Any,
        target: str,
        trigger: str,
        original_state: t.Callable,
    ):
        """Save spied object information."""
        self._sender = sender
        self._target = target
        self._trigger = trigger
        self._original_state = original_state

    def restore_state(self) -> None:
        """Undo the `WatchersSpy.spy` wrap from the sender."""
        setattr(self._sender, self._target, self._original_state)

    def __repr__(self):
        """Display instance being spied, its wrapped callable and the `nofify`'s orientation."""
        return f"Spying(sender={self._sender}, method={self._target}, trigger={self._trigger})"


class WatchersSpy(Watchers):
    """`Watchers` allowing imbuing objects with `notify` without changing them directly.

    Examples
    --------
    >>> class Food:
    ...    def cook(self, name: str):
    ...        self.name = name

    >>> class CatWatcher(AbstractWatcher):
    ...    def push(self, food: Food, *args, **kwargs):
    ...        if food.name == 'fish':
    ...            logger.debug(f'Cat loves %s!', food.name)
    ...        else:
    ...            logger.debug(f'Cat hates %s!', food.name)

    >>> class MonkeyWatcher(AbstractWatcher):
    ...    def push(self, food: Food, *args, **kwargs):
    ...        if food.name == 'banana':
    ...            logger.debug(f'Monkey loves %s!', food.name)
    ...        else:
    ...            logger.debug(f'Monkey hates %s!', food.name)


    >>> food, watchers = Food(), WatchersSpy()
    >>> watchers.attach_many([CatWatcher(), MonkeyWatcher()])
    <WatchersSpy object:Observers[CatWatcher, MonkeyWatcher]>
    >>> watchers.spy(food, 'cook')
    Spying(sender=<Food object>, method=cook, trigger=after)
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

    def __init__(self, *args, **kwargs):
        """`Watchers` initialization along with an empty structure to track spies."""
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
        instance = super().__repr__()
        return instance.replace('Watchers', 'WatchersSpy')

    def reset(self, reset_spies: bool = True) -> WatchersLite:
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
        <Watchers object:Observers[]>
        >>> watchers.spies()
        []
        """
        if reset_spies:
            self.undo_spies()
        return super().reset()

    def spy(
        self,
        sender: t.Union[t.Type[object], object],
        target: str,
        trigger: str = 'after',
    ) -> SpyContainer:
        """Imbue `notify` - after or before - the choose callable being executed.

        Parameters
        ----------
        sender : a class or instance to spy on.
        target : a method name to spy on.
        trigger : a trigger to call the `notify` method. Options are (`before`, `after`).
            * 'before' will call `notify` before the original method.
            * 'after' will call `notify` after the original method.
            * Default: 'after'.

        Examples
        --------
        >>> class Food:
        ...     def cook(self, name: str):
        ...         self.name = name

        >>> food, watchers = Food(), WatchersSpy()
        >>> watchers.attach_many([CatWatcher(), MonkeyWatcher()])
        <WatchersSpy object:Observers[CatWatcher, MonkeyWatcher]>
        >>> watchers.spy(food, 'cook')
        Spying(sender=<Food object>, method=cook, trigger=after)
        >>> food.cook('fish')
        [watchers][DEBUG][2077-12-27 00:00:00,111] >>> Notifying watcher: CatWatcher object...
        [watchers][DEBUG][2077-12-27 00:00:00,112] >>> Cat loves fish!
        [watchers][DEBUG][2077-12-27 00:00:00,113] >>> Notifying watcher: MonkeyWatcher object...
        [watchers][DEBUG][2077-12-27 00:00:00,114] >>> Monkey hates fish!
        """
        if trigger not in ('before', 'after'):
            raise SpyError(f"Trigger '{trigger}' is not supported. Options are ('before', 'after')")
        method = getattr(sender, target)

        def spy_wrapper(*args, **kwargs):
            if trigger == 'after':
                method(*args, **kwargs)
                self.notify(sender, *args, **kwargs)
            else:
                self.notify(sender, args, **kwargs)
                method(*args, **kwargs)
        setattr(sender, target, spy_wrapper)
        spy = self._container(sender, target, trigger, method)
        self._spies[(sender, target)] = spy
        self._logger.debug(f"<sender '{sender}'> <method '{target}'> is now being spied...")
        return spy

    def spies(self, as_type: t.Optional[t.Iterable] = None) -> t.Iterable[AbstractSpyContainer]:
        """Bring all spied objects.

        Parameters
        ----------
        as_type : optional cast to be applied on spied objects (*Defaut: `None`).

        Examples
        --------
        >>> class Food:
        ...     def cook(self, name: str): ...

        >>> watchers = WatchersSpy()
        >>> watchers.spy(food(), 'cook')
        >>> watchers.spies()
        [Spying(sender=<Food object>, method=cook, trigger=after)]
        >>> watchers.spies(set)
        {Spying(sender=<Food object>, method=cook, trigger=after)}
        """
        return list(self._spies.values()) if as_type is None else as_type(self._spies.values())

    def undo_spy(self, sender: t.Type, target: str) -> SpyContainer:
        """Stop spying an object by removing the `notify` wrapper applied by `spy` method.

        Parameters
        ----------
        sender : a class or instance to spy on.
        target : a method name to spy on.

        Examples
        --------
        >>> class Food:
        ...     def cook(self, name: str): ...

        >>> food, watchers = Food(), WatchersSpy()
        >>> watchers.spy(food, 'cook')
        Spying(sender=<Food object>, method=cook, trigger=after)
        >>> watchers.undo_spy(food, 'cook')
        Spying(sender=<Food object>, method=cook, trigger=after)
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

        >>> food_a, food_b, watchers = Food(), Food(),  WatchersSpy()
        >>> watchers.spy(food_a, 'cook', 'after')
        Spying(sender=<Food object>, method=cook, trigger=after)
        >>> watchers.spy(food_b, 'cook', 'before')
        Spying(sender=<Food object>, method=cook, trigger=after)
        >>> watchers.undo_spies()
        [
            Spying(sender=<Food object>, method=cook, trigger=after),
            Spying(sender=<Food object>, method=cook, trigger=before),
        ]
        """
        return [self.undo_spy(sender, target) for sender, target in tuple(self._spies.keys())]

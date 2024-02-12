import logging
import typing as t
from copy import deepcopy
from watchify import exceptions as e, functions
from watchify.logger import logger as watchify_logger
from watchify.interfaces import AbstractWatcher, AbstractWatchers


class WatchersLite(AbstractWatchers):
    """Essential watchers operations used by `Watchers` and `WatchersSpy`, easily extended."""

    def __init__(self) -> None:
        """Create an empty observers sequence."""
        self._watchers: t.List[AbstractWatcher] = []

    def __add__(self, watchers: AbstractWatchers) -> 'WatchersLite':
        """Union on both observers pool using the current instance copy as ref.

        Parameters
        ----------
        watchers : another `AbstractWatchers` concrete implementation.

        Examples
        --------
        >>> watchers_a = Watchers().attach(CatWatcher())
        >>> watchers_a
        <WatchersLite object:Observers[CatWatcher]>
        >>> watchers_b = Watchers().attach(MonkeyWatcher())
        <WatchersLite object:Observers[MonkeyWatcher]>
        >>> watchers_a + watchers_b
        <WatchersLite object:Observers[CatWatcher, MonkeyWatcher]>
        """
        output_watchers = deepcopy(self)
        output_watchers.attach_many(watchers.observers())
        return output_watchers

    def __call__(self, *args, **kwargs) -> None:
        """Notify observers.

        Examples
        --------
        >>> class Food: name = 'fish'
        ...
        >>> watchers = Watchers().attach(CatWatcher())
        >>> watchers(Food)
        [watchers][DEBUG][2077-12-27 00:00:00,111] >>> Notifying watcher: CatWatcher object.
        [watchers][DEBUG][2077-12-27 00:00:00,112] >>> Cat loves fish!
        """
        self.notify(*args, **kwargs)

    def __contains__(self, watcher: AbstractWatcher) -> bool:
        """Check if an observer exists inside pool.

        Parameters
        ----------
        watcher : `AbstractWatcher` concrete implementation.

        Examples
        --------
        >>> cat_watcher, watchers = CatWatcher(), Watchers()
        >>> watchers.attach(cat_watcher)
        <WatchersLite object:Observers[CatWatcher]>
        >>> cat_watcher in watchers
        True
        """
        return watcher in self._watchers

    def __iter__(self) -> t.Generator[AbstractWatcher, None, None]:
        """Iter through observers pool using instance itself.

        Examples
        --------
        >>> watchers = Watchers()
        >>> watchers.attach_many([CatWatcher(), MonkeyWatcher()])
        <WatchersLite object:Observers[CatWatcher, MonkeyWatcher]>
        >>> for watcher in watchers:
        ...     print(watcher)
        ...
        CatWatcher object
        MonkeyWatcher object
        """
        for watcher in self._watchers:
            yield watcher

    def __getitem__(self, index: int) -> AbstractWatcher:
        """Match an observer based on an index.

        Parameters
        ----------
        index : observer reference inside pool.

        Examples
        --------
        >>> watchers = Watchers()
        >>> watchers.attach_many([CatWatcher(), MonkeyWatcher()])
        >>> watchers[1]
        MonkeyWatcher object
        """
        return self._watchers[index]

    def __repr__(self) -> str:
        """Show canonical representation, including dynamic truncated observers sequence.

        Examples
        --------
        >>> watchers = Watchers().attach_many([CatWatcher(), MonkeyWatcher()])
        >>> watchers
        <WatchersLite object:Observers[CatWatcher, MonkeyWatcher]>
        """
        watchers = ''
        for watcher in self._watchers[:8]:
            watchers += f'{watcher.__class__.__name__}, '
        watchers = watchers[:-2]
        if self.count() > 8:
            watchers += ', ...'
        return f'<WatchersLite object:Observers[{watchers}]>'

    def count(self) -> int:
        """Bring the ongoing observers count awaiting an event.

        Examples
        --------
        >>> watchers = Watchers().attach_many([CatWatcher(), MonkeyWatcher()])
        >>> watchers.count()
        2
        """
        return len(self._watchers)

    def reset(self) -> 'WatchersLite':
        """Prune all saved observers.

        Examples
        --------
        >>> watchers = Watchers().attach_many([CatWatcher(), MonkeyWatcher()])
        >>> watchers
        <WatchersLite object:Observers[CatWatcher, MonkeyWatcher]>
        >>> watchers.reset()
        <WatchersLite object:Observers[]>
        """
        self._watchers.clear()
        return self

    def observers(
        self,
        as_type: t.Optional[t.Callable[[t.Iterable], t.Iterable]] = None,
    ) -> t.Iterable[AbstractWatcher]:
        """Bring all observers.

        Parameters
        ----------
        as_type : optional cast to be applied on listers (*Defaut: `None`).

        Examples
        --------
        >>> watchers = Watchers().attach_many([CatWatcher(), MonkeyWatcher()])
        >>> watchers.observers()
        [CatWatcher object, MonkeyWatcher object]
        >>> watchers.observers(set)
        {CatWatcher object, MonkeyWatcher object}
        """
        return self._watchers if not as_type else as_type(self._watchers)

    def attach(self, watcher: AbstractWatcher) -> 'WatchersLite':
        """Add an observer to watcher's pool to notify it about an event.

        Parameters
        ----------
        watcher : an `AbstractWatcher` concrete implementation.

        Examples
        --------
        >>> watchers = Watchers()
        >>> watchers
        <WatchersLite object:Observers[]>
        >>> watchers.attach(CatWatcher())
        <WatchersLite object:Observers[CatWatcher]>
        >>> watchers.attach(MonkeyWatcher())
        <WatchersLite object:Observers[CatWatcher, MonkeyWatcher]>
        """
        self._watchers.append(watcher)
        return self

    def attach_many(self, watchers: t.List[AbstractWatcher]) -> 'WatchersLite':
        """Add observers to watcher's pool to notify them about an event.

        Parameters
        ----------
        watchers : a sequence of `AbstractWatcher` concrete implementations.

        Examples
        --------
        >>> watchers = Watchers()
        >>> watchers
        <WatchersLite object:Observers[]>
        >>> watchers.attach_many([CatWatcher(), MonkeyWatcher()])
        <WatchersLite object:Observers[CatWatcher, MonkeyWatcher]>
        """
        self._watchers.extend(watchers)
        return self

    def detach(self, watcher: AbstractWatcher) -> 'WatchersLite':
        """Remove an observer from watcher's pool.

        Parameters
        ----------
        watcher : an `AbstractWatcher` concrete implementation.

        Examples
        --------
        >>> cat_watcher = CatWatcher()
        >>> watchers = Watchers().attach_many([cat_watcher, MonkeyWatcher()])
        >>> watchers
        <WatchersLite object:Observers[CatWatcher, MonkeyWatcher]>
        >>> watchers.detach(cat_watcher)
        <WatchersLite object:Observers[MonkeyWatcher]>
        """
        self._watchers.remove(watcher)
        return self

    def detach_many(self, watchers: t.List[AbstractWatcher]) -> 'WatchersLite':
        """Remove observers from watcher's pool.

        Parameters
        ----------
        watchers : a sequence of `AbstractWatcher` concrete implementations.

        Examples
        --------
        >>> cat_watcher, monkey_watcher = CatWatcher(), MonkeyWatcher()
        >>> watchers = Watchers().attach_many([cat_watcher, monkey_watcher])
        >>> watchers
        <WatchersLite object:Observers[CatWatcher, MonkeyWatcher]>
        >>> watchers.detach_many([cat_watcher, monkey_watcher])
        <WatchersLite object:Observers[]>
        """
        [self._watchers.remove(watcher) for watcher in watchers]
        return self

    def notify(self, sender: t.Any, *args, **kwargs) -> 'WatchersLite':
        """Notify all observers about some change that may interest them.

        Parameters
        ----------
        sender : entity being observed. Once an event happens the sender is passed
            to each observer, so they can scrutinizes it to perform their logic accordingly.
        args : additional arguments to passed to each observer.
        kwargs : additional keyword arguments to passed to each observer.

        Examples
        --------
        >>> class Food: name = 'fish'
        ...
        >>> watchers = Watchers().attach(CatWatcher())
        >>> watchers.notify(Food)
        [watchers][DEBUG][2077-12-27 00:00:00,111] >>> Notifying watcher: CatWatcher object.
        [watchers][DEBUG][2077-12-27 00:00:00,112] >>> Cat loves fish!
        """
        [watcher.push(sender, *args, **kwargs) for watcher in self._watchers]


class Watchers(WatchersLite):
    """Objects - highly decoupled - event-driven communication tool.

    Parameters
    ----------
    logger : Python's tracker to map channel processes (*Default: `watchers.logger.logger`).
    disable_logs : whether the logs should be ommited (*Default: `False`).
    validate : whether inputs of `attach`, `attach_many` and  `__add__` must be validated before
        inserting them (*Default: `True`).

    Examples
    --------
    >>> class Food:
    ...    def cook(self, name: str) -> None:
    ...        self.name = name
    ...
    >>> class CatWatcher(AbstractWatcher):
    ...    def push(self, food: Food, *args, **kwargs) -> None:
    ...        if food.name == 'fish':
    ...            logger.debug(f'Cat loves %s!', food.name)
    ...        else:
    ...            logger.debug(f'Cat hates %s!', food.name)
    ...
    >>> class MonkeyWatcher(AbstractWatcher):
    ...    def push(self, food: Food, *args, **kwargs) -> None:
    ...        if food.name == 'banana':
    ...            logger.debug(f'Monkey loves %s!', food.name)
    ...        else:
    ...            logger.debug(f'Monkey hates %s!', food.name)
    ...
    >>> food, watchers = Food(), Watchers()
    >>> watchers.attach_many([CatWatcher(), MonkeyWatcher()])
    <WatchersLite object:Observers[CatWatcher, MonkeyWatcher]>
    >>> food.cook('fish')
    >>> watchers.notify(food)
    [watchers][DEBUG][2077-12-27 00:00:00,111] >>> Notifying watcher: CatWatcher object...
    [watchers][DEBUG][2077-12-27 00:00:00,112] >>> Cat loves fish!
    [watchers][DEBUG][2077-12-27 00:00:00,113] >>> Notifying watcher: MonkeyWatcher object...
    [watchers][DEBUG][2077-12-27 00:00:00,114] >>> Monkey hates fish!
    >>> food.cook('banana')
    >>> watchers.notify(food)
    [watchers][DEBUG][2077-12-27 00:00:00,115] >>> Notifying watcher: CatWatcher object...
    [watchers][DEBUG][2077-12-27 00:00:00,116] >>> Cat hates banana!
    [watchers][DEBUG][2077-12-27 00:00:00,117] >>> Notifying watcher: MonkeyWatcher object...
    [watchers][DEBUG][2077-12-27 00:00:00,118] >>> Monkey loves banana!
    """

    def __init__(
        self,
        logger: t.Optional[logging.Logger] = None,
        disable_logs: bool = False,
        validate: bool = True,
    ) -> None:
        """`WatchersLite.__init__`, but allowing log and validation behaviours switch."""
        super().__init__()
        self._logger = logger or watchify_logger
        self._logger.disabled = disable_logs
        self._validate = validate

    def __add__(self, watchers: 'Watchers') -> 'Watchers':
        self._is_watchers(watchers) if self._validate else None
        return super().__add__(watchers)

    def __getitem__(self, index: int) -> AbstractWatcher:
        """Match an observer based on an index.

        Parameters
        ----------
        index : observer reference inside pool.

        Examples
        --------
        >>> watchers = Watchers()
        >>> watchers.attach(CatWatcher())
        >>> watchers[2]
        Traceback (most recent call last):
        ...
        WatcherError: <Watchers object:Observers[CatWatcher]> has <1> length.
        """
        try:
            return super().__getitem__(index)
        except IndexError:
            raise e.WatcherError(f'{self} has <{self.count()}> length.')

    def __repr__(self) -> str:
        """Show canonical representation, including dynamic truncated observers sequence.

        Examples
        --------
        >>> watchers = Watchers().attach_many([CatWatcher(), MonkeyWatcher()])
        >>> watchers
        <Watchers object:Observers[CatWatcher, MonkeyWatcher]>
        """
        return super().__repr__().replace('WatchersLite', 'Watchers')

    @staticmethod
    def _is_watcher(obj: t.Any) -> None:
        """Raise an exception if the provided object is not a valid observer.

        Parameters
        ----------
        obj : target be perform the `AbstractWatcher` validation.

        Examples
        ----------
        >>> Watchers._is_watcher(CatWatcher())
        >>> Watchers._is_watcher(1)
        Traceback (most recent call last):
        ...
        NotAnObserverError: Expected <class 'AbstractWatcher'>, but got <class 'int'>.
        """
        if not functions.is_watcher(obj):
            raise e.NotAnObserverError(f"Expected <class 'AbstractWatcher'>, but got {type(obj)}.")

    @staticmethod
    def _is_watchers(obj: t.Any) -> None:
        """Raise an exception if the provided object is not a valid observers manager.

        Parameters
        ----------
        obj : target be perform the `AbstractWatchers` validation.

        Examples
        ----------
        >>> Watchers._is_watcher(Watchers())
        >>> Watchers._is_watcher(1)
        Traceback (most recent call last):
        ...
        NotAnObserverError: Expected <class 'AbstractWatchers'>, but got <class 'int'>.
        """
        if not functions.is_watchers(obj):
            raise e.NotAnOrchestratorError(
                f"Expected <class 'AbstractWatchers'>, but got {type(obj)}.",
            )

    def attach(self, watcher: AbstractWatcher) -> 'Watchers':
        self._is_watcher(watcher) if self._validate else None
        super().attach(watcher)
        self._logger.debug(f'Subscribed watcher: {watcher}.')
        return self

    def attach_many(self, watchers: t.List[AbstractWatcher]) -> 'Watchers':
        [self._is_watcher(watcher) for watcher in watchers] if self._validate else None
        super().attach_many(watchers)
        self._logger.debug(f'Subscribed watchers: {watchers}.')
        return self

    def detach(self, watcher: AbstractWatcher) -> 'Watchers':
        try:
            super().detach(watcher)
        except ValueError:
            raise e.PoolError(f'Observer <{watcher}> not found in pool.')
        self._logger.debug(f'Unsubscribed watcher: {watcher}.')
        return self

    def detach_many(self, watchers: t.List[AbstractWatcher]) -> 'Watchers':
        try:
            super().detach_many(watchers)
        except ValueError:
            raise e.PoolError('One or more observers not found in pool.')
        self._logger.debug(f'Unsubscribed watchers: {watchers}.')
        return self

    def notify(
        self,
        sender: t.Any,
        *args,
        raise_exception: t.Optional[bool] = None,
        **kwargs,
    ) -> None:
        """Notify all observers about some change that may interest any of them.

        Parameters
        ----------
        sender : entity being observed. Once an event happens the sender is passed
            to each observer, so they can scrutinizes it to perform their logic accordingly.
        args : additional arguments to passed to each observer.
        raise_exception : whether to propagate an exception while pushing information to observers.
            (*Default: `None`).
        kwargs : additional keyword arguments to passed to each observer.

        Examples
        --------
        >>> class Food: name = 'fish'
        ...
        >>> watchers = Watchers().attach(CatWatcher())
        >>> watchers.notify(Food)
        [watchers][DEBUG][2077-12-27 00:00:00,111] >>> Notifying watcher: CatWatcher object.
        [watchers][DEBUG][2077-12-27 00:00:00,112] >>> Cat loves fish!
        """
        for watcher in self._watchers:
            self._logger.debug(f'Notifying watcher: {watcher}...')
            try:
                watcher.push(sender, *args, **kwargs)
            except Exception as err:
                if raise_exception:
                    raise e.PushError(repr(err))
                else:
                    self._logger.error(
                        f'Watcher: {watcher} failed to process an event. Exception: {repr(err)}.',
                    )

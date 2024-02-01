import logging
import typing as t
from copy import deepcopy
from typing import List
from watchers import functions
from watchers.abstract import AbstractWatcher, AbstractWatchers
from watchers.exceptions import NotAWatcherError, PushError, WatcherError
from watchers.logger import logger as internal_logger


class WatchersLite(AbstractWatchers):
    """Raw implementation used by `Watchers`, easily extended."""

    def __init__(self) -> None:
        """Create an empty observers sequence."""
        self._watchers: t.List[AbstractWatcher] = []

    def __add__(self, watchers: AbstractWatchers) -> 'WatchersLite':
        """Union on both observers pool.

        Parameters
        ----------
        watchers: another `AbstractWatchers` concrete implementation.

        Examples
        --------
        >>> watchers_a = Watchers().attach(CatWatcher())
        >>> watchers_a
        <Watchers object:Observers[CatWatcher]>
        >>> watchers_b = Watchers().attach(MonkeyWatcher())
        <Watchers object:Observers[MonkeyWatcher]>
        >>> watchers_a + watchers_b
        <Watchers object:Observers[CatWatcher, MonkeyWatcher]>
        """
        output_watchers = deepcopy(self)
        output_watchers.attach_many(watchers.observers())
        return output_watchers

    def __call__(self, *args, **kwargs) -> None:
        """Notify observers using instance itself.

        Examples
        --------
        >>> class Food: name = 'fish'
        >>> watchers = Watchers().attach(CatWatcher())
        >>> watchers(Food)
        [watchers][DEBUG][2077-12-27 00:00:00,111] >>> Notifying watcher: CatWatcher object.
        [watchers][DEBUG][2077-12-27 00:00:00,112] >>> Cat loves fish!
        """
        self.notify(*args, **kwargs)

    def __iter__(self) -> AbstractWatcher:
        """Iter through observers pool using instance itself.

        Examples
        --------
        >>> watchers = Watchers()
        >>> watchers.attach_many([CatWatcher(), MonkeyWatcher()])
        <Watchers object:Observers[CatWatcher, MonkeyWatcher]>
        >>> for watcher in watchers:
        ...     print(watcher)
        CatWatcher object
        MonkeyWatcher object
        """
        for watcher in self._watchers:
            yield watcher

    def __getitem__(self, index: int) -> AbstractWatcher:
        """Fetch an observer by position using instance itself.

        Parameters
        ----------
        index: observer reference inside pool.

        Examples
        --------
        >>> watchers = Watchers()
        >>> watchers.attach_many([CatWatcher(), MonkeyWatcher()])
        >>> watchers[1]
        MonkeyWatcher object
        """
        try:
            return self._watchers[index]
        except IndexError:
            raise WatcherError(f'{self} has <{self.count()}> length.')

    def __repr__(self) -> str:
        """Show canonical representation, including dynamic truncated observers sequence.

        Examples
        --------
        >>> watchers = Watchers().attach_many([CatWatcher(), MonkeyWatcher()])
        >>> watchers
        <Watchers object:Observers[CatWatcher, MonkeyWatcher]>
        """
        watchers = ''
        for watcher in self._watchers[:8]:
            watchers += f'{watcher.__class__.__name__}, '
        watchers = watchers[:-2]
        if self.count() > 8:
            watchers += ', ...'
        return f'<Watchers object:Observers[{watchers}]>'

    def count(self) -> int:
        """Bring the current observers count.

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
        <Watchers object:Observers[CatWatcher, MonkeyWatcher]>
        >>> watchers.reset()
        >>> watchers
        <Watchers object:Observers[]>
        """
        self._watchers.clear()
        return self

    def observers(self, as_type: t.Optional[t.Iterable] = None) -> t.Iterable[AbstractWatcher]:
        """Bring all observers.

        Parameters
        ----------
        as_type : optional cast to be applied on listers (*Defaut: `None`).

        Examples
        --------
        >>> watchers = Watchers().attach_many([CatWatcher(), MonkeyWatcher()])
        >>> watchers.watchers()
        [CatWatcher object, MonkeyWatcher object]
        >>> watchers.observers(set)
        {CatWatcher object, MonkeyWatcher object}
        """
        return self._watchers if not as_type else as_type(self._watchers)

    def attach(self, watcher: AbstractWatcher) -> 'WatchersLite':
        """Add an observer to watcher's pool to notify it about an event.

        Parameters
        ----------
        watcher: an `AbstractWatcher` concrete implementation.

        Examples
        --------
        >>> watchers = Watchers()
        >>> watchers
        <Watchers object:Observers[]>
        >>> watchers.attach(CatWatcher())
        <Watchers object:Observers[CatWatcher]>
        >>> watchers.attach(MonkeyWatcher())
        <Watchers object:Observers[CatWatcher, MonkeyWatcher]>
        """
        self._watchers.append(watcher)
        return self

    def attach_many(self, watchers: t.List[AbstractWatcher]) -> 'WatchersLite':
        """Add observers to watcher's pool to notify them about an event.

        Parameters
        ----------
        watchers: a sequence of `AbstractWatcher` concrete implementations.

        Examples
        --------
        >>> watchers = Watchers()
        >>> watchers
        <Watchers object:Observers[]>
        >>> watchers.attach_many([CatWatcher(), MonkeyWatcher()])
        <Watchers object:Observers[CatWatcher, MonkeyWatcher]>
        """
        self._watchers.extend(watchers)
        return self

    def detach(self, watcher: AbstractWatcher) -> 'WatchersLite':
        """Remove an observer from watcher's pool.

        Parameters
        ----------
        watcher: an `AbstractWatcher` concrete implementation.

        Examples
        --------
        >>> cat_watcher = CatWatcher()
        >>> watchers = Watchers().attach_many([cat_watcher, MonkeyWatcher()])
        >>> watchers
        <Watchers object:Observers[CatWatcher, MonkeyWatcher]>
        >>> watchers.detach(cat_watcher)
        <Watchers object:Observers[MonkeyWatcher]>
        """
        self._watchers.remove(watcher)
        return self

    def detach_many(self, watchers: t.List[AbstractWatcher]) -> 'WatchersLite':
        """Remove observers from watcher's pool.

        Parameters
        ----------
        watchers: a sequence of `AbstractWatcher` concrete implementations.

        Examples
        --------
        >>> cat_watcher, monkey_watcher = CatWatcher(), MonkeyWatcher()
        >>> watchers = Watchers().attach_many([cat_watcher, monkey_watcher])
        >>> watchers
        <Watchers object:Observers[CatWatcher, MonkeyWatcher]>
        >>> watchers.detach_many([cat_watcher, monkey_watcher])
        <Watchers object:Observers[]>
        """
        [self._watchers.remove(watcher) for watcher in watchers]
        return self

    def notify(self, sender: t.Any, *args, **kwargs) -> 'WatchersLite':
        """Notify all observers about some change that may interest any of them.

        Parameters
        ----------
        sender : entity being observed. Once an event happens the sender is passed
            to each observer, so they can scrutinizes it to perform their logic accordingly.
        args : additional arguments to passed to each observer.
        kwargs : additional keyword arguments to passed to each observer.

        Examples
        --------
        >>> class Food: name = 'fish'
        >>> watchers = Watchers().attach(CatWatcher())
        >>> watchers.notify(Food)
        [watchers][DEBUG][2077-12-27 00:00:00,111] >>> Notifying watcher: CatWatcher object.
        [watchers][DEBUG][2077-12-27 00:00:00,112] >>> Cat loves fish!
        """
        [watcher.push(sender, *args, **kwargs) for watcher in self._watchers]


class Watchers(WatchersLite):
    """Objects decoupled event-driven communication tool.

    Parameters
    ----------
    logger : Python's tracker to map channel processes (*Default: `watchers.logger.logger`).
    disable_logs : whether the logs should be ommited (*Default: `False`).
    validate : whether inputs of `attach`, `attach_many` and  `__add__` must be validated before
        inserting them (*Default: `True`).

    Examples
    --------
    class Food:
        def cook(self, name: str):
            self.name = name

    class CatWatcher(AbstractWatcher):
        def push(self, food: Food, *args, **kwargs):
            if food.name == 'fish':
                logger.debug(f'Cat loves %s!', food.name)
            else:
                logger.debug(f'Cat hates %s!', food.name)

    class MonkeyWatcher(AbstractWatcher):
        def push(self, food: Food, *args, **kwargs):
            if food.name == 'banana':
                logger.debug(f'Monkey loves %s!', food.name)
            else:
                logger.debug(f'Monkey hates %s!', food.name)


    >>> food, watchers = Food(), Watchers()
    >>> watchers.attach_many([CatWatcher(), MonkeyWatcher()])
    <Watchers object:Observers[CatWatcher, MonkeyWatcher]>
    >>> food.cook('fish')
    [watchers][DEBUG][2077-12-27 00:00:00,111] >>> Notifying watcher: CatWatcher object.
    [watchers][DEBUG][2077-12-27 00:00:00,112] >>> Cat loves fish!
    [watchers][DEBUG][2077-12-27 00:00:00,113] >>> Notifying watcher: MonkeyWatcher object.
    [watchers][DEBUG][2077-12-27 00:00:00,114] >>> Monkey hates fish!
    >>> food.cook('banana')
    [watchers][DEBUG][2077-12-27 00:00:00,115] >>> Notifying watcher: CatWatcher object.
    [watchers][DEBUG][2077-12-27 00:00:00,116] >>> Cat hates banana!
    [watchers][DEBUG][2077-12-27 00:00:00,117] >>> Notifying watcher: MonkeyWatcher object.
    [watchers][DEBUG][2077-12-27 00:00:00,118] >>> Monkey loves banana!
    """

    def __init__(
        self,
        logger: t.Optional[logging.Logger] = None,
        disable_logs: bool = False,
        validate: bool = True,
    ):
        super().__init__()
        self._logger = logger or internal_logger
        self._logger.disabled = disable_logs
        self._validate = validate

    @staticmethod
    def _is_watcher(obj: t.Any):
        """Raise an exception if the provided object is not a valid observer."""
        if not functions.is_watcher(obj):
            raise NotAWatcherError(f"Expected <class 'AbstractWatcher'>, but got {type(obj)}.")

    @staticmethod
    def _is_watchers(obj: t.Any):
        """Raise an exception if the provided object is not a valid observer manager."""
        if not functions.is_watchers(obj):
            raise NotAWatcherError(f"Expected <class 'AbstractWatchers'>, but got {type(obj)}.")

    def __add__(self, watchers: 'Watchers') -> 'Watchers':
        self._is_watchers(watchers) if self._validate else None
        return super().__add__(watchers)

    def attach(self, watcher: AbstractWatcher) -> 'Watchers':
        self._is_watcher(watcher) if self._validate else None
        super().attach(watcher)
        self._logger.debug(f'Subscribed watcher: {watcher}.')
        return self

    def attach_many(self, watchers: List[AbstractWatcher]) -> 'Watchers':
        [self._is_watcher(watcher) for watcher in watchers] if self._validate else None
        super().attach_many(watchers)
        self._logger.debug(f'Subscribed watchers: {watchers}.')
        return self

    def detach(self, watcher: AbstractWatcher) -> 'Watchers':
        super().detach(watcher)
        self._logger.debug(f'Unsubscribed watcher: {watcher}.')

    def detach_many(self, watchers: List[AbstractWatcher]) -> 'Watchers':
        super().detach_many(watchers)
        self._logger.debug(f'Unsubscribed watchers: {watchers}.')

    def notify(
        self,
        sender: t.Any,
        *args,
        raise_exception: t.Optional[bool] = None,
        **kwargs,
    ) -> 'Watchers':
        for watcher in self._watchers:
            self._logger.debug(f'Notifying watcher: {watcher}.')
            try:
                watcher.push(sender, *args, **kwargs)
            except Exception as e:
                if raise_exception:
                    raise PushError(repr(e))
                else:
                    self._logger.error(f'Watcher: {watcher} failed to process an event. Exception: {repr(e)}.')

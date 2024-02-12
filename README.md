<h1 align="center">Watchify</h1>


                                    ⠀⠀⠀⠀⠀⠀⢀⠀⠀⠀⠀⠀⠀⢠⡆⠀⠀⠀⠀⠀⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀
                                    ⠀⠀⠀⠀⠀⠀⠈⣷⣄⠀⠀⠀⠀⣾⣷⠀⠀⠀⠀⣠⣾⠃⠀⠀⠀⠀⠀⠀⠀⠀
                                    ⠀⠀⠀⠀⠀⠀⠀⢿⠿⠃⠀⠀⠀⠉⠉⠁⠀⠀⠐⠿⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀
                                    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣠⣤⣤⣶⣶⣶⣤⣤⣄⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                                    ⠀⠀⠀⠀⠀⢀⣤⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣦⣄⠀⠀⠀⠀⠀⠀
                                    ⠀⠀⠀⣠⣶⣿⣿⡿⣿⣿⣿⡿⠋⠉⠀⠀⠉⠙⢿⣿⣿⡿⣿⣿⣷⣦⡀⠀⠀⠀
                                    ⠀⢀⣼⣿⣿⠟⠁⢠⣿⣿⠏⠀⠀⢠⣤⣤⡀⠀⠀⢻⣿⣿⡀⠙⢿⣿⣿⣦⠀⠀
                                    ⣰⣿⣿⡟⠁⠀⠀⢸⣿⣿⠀⠀⠀⢿⣿⣿⡟⠀⠀⠈⣿⣿⡇⠀⠀⠙⣿⣿⣷⡄
                                    ⠈⠻⣿⣿⣦⣄⠀⠸⣿⣿⣆⠀⠀⠀⠉⠉⠀⠀⠀⣸⣿⣿⠃⢀⣤⣾⣿⣿⠟⠁
                                    ⠀⠀⠈⠻⣿⣿⣿⣶⣿⣿⣿⣦⣄⠀⠀⠀⢀⣠⣾⣿⣿⣿⣾⣿⣿⡿⠋⠁⠀⠀
                                    ⠀⠀⠀⠀⠀⠙⠻⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠛⠁⠀⠀⠀⠀⠀
                                    ⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠛⠛⠿⠿⠿⠿⠿⠿⠛⠋⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀
                                    ⠀⠀⠀⠀⠀⠀⠀⢰⣷⡦⠀⠀⠀⢀⣀⣀⠀⠀⠀⢴⣾⡇⠀⠀⠀⠀⠀⠀⠀⠀
                                    ⠀⠀⠀⠀⠀⠀⠀⣸⠟⠁⠀⠀⠀⠘⣿⡇⠀⠀⠀⠀⠙⢷⠀⠀⠀⠀⠀⠀⠀⠀
                                    ⠀⠀⠀⠀⠀⠀⠀⠁⠀⠀⠀⠀⠀⠀⠻⠀⠀⠀⠀⠀⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀

***

<p align="center">
  <a href='https://coveralls.io/github/daniel-augustus/watchify?branch=main'><img src='https://coveralls.io/repos/github/daniel-augustus/watchify/badge.svg?branch=main' alt='Coverage Status' /></a>
  <img alt="License" src="https://img.shields.io/badge/License-MIT-blue.svg">
  <img alt="Python Version" src="https://img.shields.io/badge/Python-^3.8.1-blue.svg">
  <a href="https://pypi.org/project/watchify/">
    <img alt="PyPi" src="https://img.shields.io/badge/PyPi-0.2.0-yellow.svg">
  </a>
</p>

***

## About

`watchify` is an **event-driven** inter-object communication tool, promoting the **segregation of
complex functionalities** into smaller ones while enabling their relationship through a third-party entity.
This approach promotes **loosely coupled** implementations, simplifying **Single Responsibility Principle** commitment yet keeping a **cohesive code**.
As a result, the code becomes more flexible, maintainable, testable, and overrall healthier.

## Install

```console
$ pip install watchify
```

## Usage

```python
from watchify import AbstractWatcher, Watchers
from watchify.logger import logger


class Food:
    def cook(self, name: str) -> None:
        self.name = name


class CatWatcher(AbstractWatcher):
    def push(self, food: Food, *args, **kwargs) -> None:
        if food.name == 'fish':
            logger.debug(f'Cat loves %s!', food.name)
        else:
            logger.debug(f'Cat hates %s!', food.name)


class MonkeyWatcher(AbstractWatcher):
    def push(self, food: Food, *args, **kwargs) -> None:
        if food.name == 'banana':
            logger.debug(f'Monkey loves %s!', food.name)
        else:
            logger.debug(f'Monkey hates %s!', food.name)


>>> food, watchers = Food(), Watchers()
>>> watchers.attach_many([CatWatcher(), MonkeyWatcher()])
<Watchers object:Observers[CatWatcher, MonkeyWatcher]>
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
```

Or using `WatchersSpy`, you can notify listeners automatically whenever a specified constraint is
met, so you don't need to manually invoke `notify` as shown above:

```python
from watchify import AbstractWatcher, WatchersSpy
from watchify.logger import logger

# [...]

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
```

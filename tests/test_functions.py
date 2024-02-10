from watchify import functions


def test_is_watcher(cat_watcher):
    assert functions.is_watcher(cat_watcher) is True

import pytest


@pytest.fixture
def food_sender() -> object:
    """Create a generic object to act as sender for observers."""
    class Food:
        def cook(self, name: str) -> None:
            self.name = name

    return Food()

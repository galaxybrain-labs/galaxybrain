import pytest

from tests.mocks.mock_driver_config import MockDriverConfig


@pytest.fixture(autouse=True)
def mock_event_bus():
    from griptape.events import event_bus

    event_bus.clear_event_listeners()

    yield event_bus

    event_bus.clear_event_listeners()


@pytest.fixture(autouse=True)
def mock_config(request):
    from griptape.config import config

    config.reset()

    # Some tests we don't want to use the autouse fixture's MockDriverConfig
    if "skip_autouse_fixture" in request.keywords:
        yield

        return

    config.drivers = MockDriverConfig()

    yield config

    config.reset()

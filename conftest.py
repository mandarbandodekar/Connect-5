import pytest

from app import create_app

@pytest.fixture
def app():
    apps = create_app()
    return apps

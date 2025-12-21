"""
Pytest configuration and fixtures for BarberAppClient tests.
"""
import os
import sys

# Mock config module before importing barberapp_client
# This allows tests to run without a real config.py file
class MockConfig:
    BARBER_ID = "test_shop_id"
    USERNAME = "test_user"
    PASSWORD = "test_pass"
    PREFERRED_BARBER = "TestBarber"
    PREFERRED_SERVICE_ID = 0
    TELEGRAM_BOT_TOKEN = ""
    TELEGRAM_CHAT_ID = ""

sys.modules['config'] = MockConfig()

import pytest
import responses

# Add parent directory to path to import barberapp_client
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from barberapp_client import BarberAppClient, search_nearby


# =============================================================================
# MOCK DATA
# =============================================================================

MOCK_BARBERS = [
    {
        "Id": 1,
        "Nome": "Giovanni",
        "Nascosto": False,
        "MinutiTaglio": 45,
        "MinutiTaglioArr": [45, 15, 15, 15, 30, 45, 30, 30, 60, 30, 45]
    },
    {
        "Id": 2,
        "Nome": "Marco",
        "Nascosto": False,
        "MinutiTaglio": 45,
        "MinutiTaglioArr": [45, 15, 15, 15, 30, 45, 30, 30, 60, 30, 45]
    },
    {
        "Id": 3,
        "Nome": "Hidden",
        "Nascosto": True,
        "MinutiTaglio": 45,
        "MinutiTaglioArr": [45, 15, 15, 15, 30, 45, 30, 30, 60, 30, 45]
    }
]

MOCK_SERVICES = {
    "Nome": [
        "Taglio normale + shampoo",
        "Colore",
        "Sopracciglia",
        "Barba corta",
        "",
        "Taglio pettine e forbice",
        "",
        "",
        "",
        "",
        "Taglio + barba"
    ],
    "Prezzo": [13.0, 0.0, 4.0, 5.0, 0.0, 15.0, 0.0, 0.0, 0.0, 0.0, 18.0],
    "Descrizione": ["", "", "", "", "", "", "", "", "", "", ""]
}

MOCK_SCHEDULE = [
    {
        "Gi": "231225",  # 23/12/25
        "Pa": "Giovanni",
        "Fe": False,
        "Pr": [
            {"Or": "2312251115", "Sl": 45},
            {"Or": "2312251200", "Sl": 30},
            {"Or": "2312251530", "Sl": 60}
        ]
    },
    {
        "Gi": "231225",
        "Pa": "Marco",
        "Fe": False,
        "Pr": [
            {"Or": "2312251000", "Sl": 45}
        ]
    },
    {
        "Gi": "241225",  # 24/12/25 - holiday
        "Pa": "Giovanni",
        "Fe": True,
        "Pr": []
    }
]

MOCK_CONFIRMED_RESERVATIONS = [
    {
        "Or": "2312251115",
        "Pa": "Giovanni",
        "Ti": 0
    }
]

MOCK_PENDING_RESERVATIONS = [
    {
        "Or": "241225",
        "Pa": "Giovanni"
    }
]


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def mock_client():
    """Create a BarberAppClient with mocked credentials for unit tests."""
    return BarberAppClient(
        user_id="test_shop_id",
        username="test_user",
        password="test_pass"
    )


@pytest.fixture
def real_client():
    """Create a BarberAppClient with real credentials from config.py for integration tests."""
    # Load the actual config.py file from disk, bypassing our mock
    import importlib.util
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.py")
    
    # Skip if config.py doesn't exist
    if not os.path.exists(config_path):
        pytest.skip("config.py not found - skipping integration tests")
    
    spec = importlib.util.spec_from_file_location("real_config", config_path)
    real_config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(real_config)
    
    return BarberAppClient(
        user_id=real_config.BARBER_ID,
        username=real_config.USERNAME,
        password=real_config.PASSWORD
    )


@pytest.fixture
def mocked_responses():
    """Activate responses mock for HTTP requests."""
    with responses.RequestsMock() as rsps:
        yield rsps

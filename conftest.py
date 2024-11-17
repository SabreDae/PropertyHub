import os
import django
import pytest

def pytest_configure():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'property_hub.settings.development')
    django.setup()

@pytest.fixture(autouse=True)
def _setup_printing():
    import sys
    import io
    sys.stdout = sys.__stdout__
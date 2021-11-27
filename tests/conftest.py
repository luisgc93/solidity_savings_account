import pytest
from datetime import datetime, timedelta

@pytest.fixture
def target_date():
    return datetime.now() + timedelta(days=15)

import pytest
from datetime import datetime, timedelta
from brownie import network
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS

@pytest.fixture
def target_date():
    return datetime.now() + timedelta(days=15)

def dev_only(func):
    def check_network():
     if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
 
    return check_network 
from datetime import datetime, timedelta
from freezegun import freeze_time
import pytest
import time
from brownie import network
from scripts.deploy import deploy_savings_account
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account


def test_transfers_and_withdraws_funds_when_conditions_are_valid():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    target_date = datetime.now() + timedelta(days=15)
    account = get_account()
    savings_account_contract = deploy_savings_account(target_date.timestamp())

    account.transfer(savings_account_contract.address, "1 gwei")
    time.sleep(60)

    assert savings_account_contract.balance() == 1000_000_000

    future_date = target_date + timedelta(days=1)
    with freeze_time(future_date.isoformat()):
        savings_account_contract.withdraw()

        assert savings_account_contract.balance() == 0

import pytest
import time
from freezegun import freeze_time
from datetime import datetime, timedelta
from brownie import network
from brownie.exceptions import VirtualMachineError
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, get_contract
from scripts.deploy import deploy_savings_account


def test_cannot_deploy_if_target_date_is_in_the_past():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    target_date_timestamp = time.time() - 1000
    
    with pytest.raises(VirtualMachineError):
        deploy_savings_account(target_date_timestamp)

def test_can_deploy_if_target_date_is_in_the_future():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    target_date_timestamp = time.time() + 1000
    
    savings_account_contract = deploy_savings_account(target_date_timestamp)
    
    assert savings_account_contract.owner() == get_account().address

def test_updates_contract_balance_and_eth_break_even_price_when_funded():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    target_date_timestamp = time.time() + 1000
    account = get_account()
    savings_account_contract = deploy_savings_account(target_date_timestamp)
    
    tx = account.transfer(savings_account_contract.address, "1 ether")
    tx.wait(1)
    
    assert savings_account_contract.balance() == 10**18


def test_cannot_withdraw_if_target_date_is_in_the_future_and_current_eth_price_is_not_gt_break_even_price():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    target_date_timestamp = time.time() + 1000
    account = get_account()
    savings_account_contract = deploy_savings_account(target_date_timestamp)
    
    tx = account.transfer(savings_account_contract.address, "1 ether")
    tx.wait(1)

    new_price  = savings_account_contract.getLatestPrice() - 1000
    get_contract("eth_usd_price_feed").updateAnswer(new_price)
    
    with pytest.raises(VirtualMachineError) as e:
        savings_account_contract.withdraw()

def test_can_withdraw_if_target_date_is_in_the_past():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    target_date_timestamp = time.time() + 1000
    account = get_account()
    savings_account_contract = deploy_savings_account(target_date_timestamp)
    
    tx = account.transfer(savings_account_contract.address, "1 ether")
    tx.wait(1)

    future_date = datetime.now() + timedelta(days=30)
    with freeze_time(future_date.isoformat()):
        savings_account_contract.withdraw()

        assert savings_account_contract.balance() == 0

def test_can_withdraw_if_current_eth_price_is_gt_break_even_price():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    target_date_timestamp = time.time() + 1000
    account = get_account()
    savings_account_contract = deploy_savings_account(target_date_timestamp)
    
    tx = account.transfer(savings_account_contract.address, "1 ether")
    tx.wait(1)
    savings_account_contract.withdraw()

    assert savings_account_contract.balance() == 0

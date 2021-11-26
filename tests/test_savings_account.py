import pytest
import time
from brownie import network
from brownie.exceptions import VirtualMachineError
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account
from scripts.deploy import deploy_savings_account


def test_cannot_deploy_if_target_date_is_in_the_past():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    target_date_in_unix = 1606346617
    with pytest.raises(VirtualMachineError):
        deploy_savings_account(target_date_in_unix)

def test_can_deploy_if_target_date_is_in_the_future():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    target_date_in_unix = time.time() + 1000
    savings_account_contract = deploy_savings_account(target_date_in_unix)
    
    assert savings_account_contract.owner() == get_account().address

def test_updates_contract_balance_and_eth_break_even_price_when_funded():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    target_date_in_unix = time.time() + 1000
    account = get_account()
    savings_account_contract = deploy_savings_account(target_date_in_unix)
    
    account.transfer(savings_account_contract.address, "1 ether")
    assert savings_account_contract.balance() == 10**18


def test_cannot_withdraw_if_target_date_is_in_the_future_and_current_eth_price_is_lt_break_even_price():
    pass

def test_can_withdraw_if_target_date_is_in_the_past():
    pass

def test_can_withdraw_if_current_eth_price_is_gt_break_even_price():
    pass
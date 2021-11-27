import pytest
from datetime import datetime, timedelta
from brownie.exceptions import VirtualMachineError
from conftest import dev_only
from scripts.helpful_scripts import (
    get_account,
    get_contract,
)
from scripts.deploy import deploy_savings_account, deploy_savings_account_mock


@dev_only
def test_cannot_deploy_if_target_date_is_in_the_past():
    target_date = datetime.now() - timedelta(days=15)

    with pytest.raises(VirtualMachineError):
        deploy_savings_account(target_date.timestamp())


@dev_only
def test_can_deploy_if_target_date_is_in_the_future(target_date):
    savings_account_contract = deploy_savings_account(target_date.timestamp())

    assert savings_account_contract.owner() == get_account().address


@dev_only
def test_updates_contract_balance_and_break_even_price_when_funded(target_date):
    account = get_account()
    savings_account_contract = deploy_savings_account(target_date.timestamp())

    tx = account.transfer(savings_account_contract.address, "1 ether")
    tx.wait(1)

    assert savings_account_contract.balance() == 10 ** 18
    assert savings_account_contract.ethBreakEvenPrice() == 2000 * 10**18


@dev_only
def test_updates_break_even_price_when_funded_multiple_times_at_different_prices(target_date):
    account = get_account()
    savings_account_contract = deploy_savings_account(target_date.timestamp())

    tx = account.transfer(savings_account_contract.address, "1 ether")
    tx.wait(1)
    new_price = savings_account_contract.getLatestPrice() - 1000_000_000_000_000_000_000
    get_contract("eth_usd_price_feed").updateAnswer(new_price)
    tx = account.transfer(savings_account_contract.address, "1 ether")
    tx.wait(1)

    new_expected_avg_price = 1500 * 10**18 
    assert savings_account_contract.ethBreakEvenPrice() == new_expected_avg_price

@dev_only
def test_cannot_withdraw_if_target_date_is_in_the_future_and_current_eth_price_is_not_gt_break_even_price(target_date):
    account = get_account()
    savings_account_contract = deploy_savings_account(target_date.timestamp())

    tx = account.transfer(savings_account_contract.address, "1 ether")
    tx.wait(1)

    new_price = savings_account_contract.getLatestPrice() - 1000
    get_contract("eth_usd_price_feed").updateAnswer(new_price)

    with pytest.raises(VirtualMachineError):
        savings_account_contract.withdraw({"from": account})


@dev_only
def test_can_withdraw_if_target_date_is_in_the_past(target_date):
    account = get_account()
    savings_account_contract = deploy_savings_account_mock(target_date.timestamp())

    tx = account.transfer(savings_account_contract.address, "1 ether")
    tx.wait(1)

    future_date = target_date + timedelta(days=1)
    savings_account_contract.setCurrentDate(future_date.timestamp())
    savings_account_contract.withdraw({"from": account})

    assert savings_account_contract.balance() == 0


@dev_only
def test_can_withdraw_if_current_eth_price_is_gt_break_even_price(target_date):
    account = get_account()
    savings_account_contract = deploy_savings_account(target_date.timestamp())

    tx = account.transfer(savings_account_contract.address, "1 ether")
    tx.wait(1)
    new_price = savings_account_contract.getLatestPrice() + 1000
    get_contract("eth_usd_price_feed").updateAnswer(new_price)
    
    savings_account_contract.withdraw({"from": account})

    assert savings_account_contract.balance() == 0

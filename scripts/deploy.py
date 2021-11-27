from datetime import datetime, timedelta
from brownie import config, network, MockV3Aggregator, SavingsAccount, SavingsAccountMock
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    deploy_mocks,
    get_account,
)


def deploy_savings_account(target_date_timestamp):
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        deploy_mocks()
        price_feed_address = MockV3Aggregator[-1].address
    else:
        price_feed_address = config["networks"][network.show_active()][
            "eth_usd_price_feed"
        ]

    account = get_account()
    print(f"Deploying to {account.address}!")
    savings_account = SavingsAccount.deploy(
        price_feed_address,
        target_date_timestamp,
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )

    print(f"Contract deployed to {savings_account.address}")
    return savings_account

def deploy_savings_account_mock(target_date_timestamp):
    # for testing purposes
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        print("This should only be used in a development network. Exiting")
        return
    
    deploy_mocks()
    price_feed_address = MockV3Aggregator[-1].address
    account = get_account()
    print(f"Deploying to {account.address}!")
    savings_account_mock = SavingsAccountMock.deploy(
        price_feed_address,
        target_date_timestamp,
        {"from": account},
    )

    print(f"Contract deployed to {savings_account_mock.address}")
    return savings_account_mock


def main():
    target_date = datetime.now() + timedelta(days=365)
    deploy_savings_account(target_date.timestamp())

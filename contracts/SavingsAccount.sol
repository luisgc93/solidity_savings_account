// SPDX-License-Identifier: MIT

pragma solidity >=0.8 <0.9.0;

import "./PriceFeedConsumer.sol";


contract SavingsAccount is PriceFeedConsumer {

    address public owner;
    uint256 public currentDate;
    uint256 public targetDate;
    uint256 public currentEthPrice;
    uint256 public ethBreakEvenPrice = 0;
    uint256 public fundsCounter; // count how many times the contract has been funded
    event ValueReceived(address user, uint256 amount, uint256 totalBalance);


    constructor(address _priceFeed, uint256 _targetDate) PriceFeedConsumer(_priceFeed) {
        owner = msg.sender;
        currentDate = block.timestamp;
        currentEthPrice = uint256(getLatestPrice());
        require(_targetDate > currentDate);
        targetDate = _targetDate;
    }

    // Anyone can fund the contract
    receive () external payable {
        emit ValueReceived(msg.sender, msg.value, address(this).balance);
        fundsCounter++;
        currentEthPrice = uint256(getLatestPrice());
        ethBreakEvenPrice = ethBreakEvenPrice + currentEthPrice / fundsCounter;
    }

    function withdraw() public payable {
        require(msg.sender == owner);
        currentEthPrice = uint256(getLatestPrice());
        currentDate = block.timestamp;
        require(currentEthPrice >= ethBreakEvenPrice || currentDate >= targetDate);
        payable(owner).transfer(address(this).balance);
    }
}
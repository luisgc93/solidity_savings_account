// SPDX-License-Identifier: MIT

pragma solidity >=0.8 <0.9.0;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";


contract SavingsAccount { // is PriceFeedConsumer ?

    address public owner;
    uint256 public currentDate;
    uint256 public targetDate;
    uint256 public currentEthPrice;
    uint256 public ethBreakEvenPrice = 0;
    uint256 public fundsCounter; // count how many times the contract has been funded
    AggregatorV3Interface public priceFeed;
    event ValueReceived(address user, uint256 amount, uint256 totalBalance);


    constructor(address _priceFeed, uint256 _targetDate) {
        owner = msg.sender;
        priceFeed = AggregatorV3Interface(_priceFeed);
        currentDate = block.timestamp;
        currentEthPrice = getPrice();
        require(_targetDate > currentDate);
        targetDate = _targetDate;
    }

    // Anyone can fund the contract
    receive () external payable {
        emit ValueReceived(msg.sender, msg.value, address(this).balance);
        fundsCounter++;
        currentEthPrice = getPrice();
        ethBreakEvenPrice = ethBreakEvenPrice + currentEthPrice / fundsCounter;
    }

    function getPrice() public view returns (uint256) {
        (, int256 price, , , ) = priceFeed.latestRoundData();
        return uint256(price * 10_000_000_000);
    }

    function withdraw() public payable {
        require(msg.sender == owner);
        currentEthPrice = getPrice();
        currentDate = block.timestamp;
        require(currentEthPrice >= ethBreakEvenPrice || currentDate >= targetDate);
        payable(owner).transfer(address(this).balance);
    }
}
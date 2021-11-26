// SPDX-License-Identifier: MIT

pragma solidity >=0.8 <0.9.0;

import "./PriceFeedConsumer.sol";


contract SavingsAccount is PriceFeedConsumer {

    address public owner;
    uint256 public currentDate;
    uint256 public targetDate;
    uint256 public currentEthPrice;
    uint256 public ethBreakEvenPrice = 0;
    uint256[] public pricesFunded;
    uint256[] public valuesFunded;


    constructor(address _priceFeed, uint256 _targetDate) PriceFeedConsumer(_priceFeed) {
        owner = msg.sender;
        currentDate = block.timestamp;
        currentEthPrice = uint256(getLatestPrice());
        require(_targetDate > currentDate);
        targetDate = _targetDate;
    }

    // Anyone can fund the contract
    receive () external payable {
        currentEthPrice = uint256(getLatestPrice());
        pricesFunded.push(currentEthPrice);
        valuesFunded.push(msg.value);
        calculateEthBEP();
    }

  
  function calculateEthBEP() public {
      // BEP = SUM(amount * price)/balance
      require(pricesFunded.length == valuesFunded.length);
      uint256 valueTimesPriceSum = 0;
      for (uint256 i=0; i < pricesFunded.length ; i++) {
          valueTimesPriceSum += valuesFunded[i] * pricesFunded[i];
        }
        ethBreakEvenPrice = valueTimesPriceSum/address(this).balance;
  }
  
  function withdraw() public payable {
        require(msg.sender == owner);
        currentEthPrice = uint256(getLatestPrice());
        currentDate = block.timestamp;
        require(currentEthPrice >= ethBreakEvenPrice || currentDate >= targetDate);
        payable(owner).transfer(address(this).balance);
    }
}
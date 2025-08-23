// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract PriceMonitor {
    event PriceUpdated(address indexed updater, uint256 price, uint256 ts);
    uint256 public lastPrice;
    uint256 public lastUpdated;
    address public owner;

    modifier onlyOwner(){require(msg.sender==owner,'not owner');_;}

    constructor(){owner=msg.sender;}

    function setPrice(uint256 p) external onlyOwner {
        lastPrice = p; lastUpdated = block.timestamp; emit PriceUpdated(msg.sender,p,lastUpdated);
    }

    function getPrice() external view returns (uint256 price, uint256 ts){
        return (lastPrice,lastUpdated);
    }
}

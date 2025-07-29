// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "./lib/AEONMath.sol";

/**
 * @title AEONMathTester
 * @dev Test contract to expose AEONMathStandalone library functions for testing
 */
contract AEONMathTester {
    using AEONMathStandalone for uint256;

    /**
     * @dev Calculate spread in basis points between two prices
     */
    function calculateSpreadBps(uint256 price1, uint256 price2) external pure returns (int256) {
        require(price2 > 0, "Division by zero");
        return AEONMathStandalone.calculateSpreadBps(price1, price2);
    }

    /**
     * @dev Check if spread is above threshold after accounting for fees
     */
    function isAboveThreshold(int256 spreadBps, uint256 feeBps) external pure returns (bool) {
        return AEONMathStandalone.isAboveThreshold(spreadBps, feeBps);
    }

    /**
     * @dev Calculate Balancer implied price
     */
    function getBalancerImpliedPrice(
        uint256 balanceIn,
        uint256 balanceOut,
        uint256 weightIn,
        uint256 weightOut
    ) external pure returns (uint256) {
        return AEONMathStandalone.getBalancerImpliedPrice(balanceIn, balanceOut, weightIn, weightOut);
    }

    /**
     * @dev Calculate efficiency score
     */
    function efficiencyScore(
        uint256 expectedProfitUSD,
        uint256 gasUsed,
        uint256 gasPriceWei
    ) external pure returns (int256) {
        return AEONMathStandalone.efficiencyScore(expectedProfitUSD, gasUsed, gasPriceWei);
    }

    /**
     * @dev Test helper: Get current block timestamp
     */
    function getCurrentTimestamp() external view returns (uint256) {
        return block.timestamp;
    }

    /**
     * @dev Test helper: Get current block number
     */
    function getCurrentBlockNumber() external view returns (uint256) {
        return block.number;
    }
}

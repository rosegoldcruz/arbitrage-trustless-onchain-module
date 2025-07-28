// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/utils/math/SafeMath.sol";

/**
 * @title SpreadCalculator
 * @dev Advanced spread calculation and arbitrage opportunity detection
 * Enforces 23bps minimum fee threshold and real-time spread monitoring
 */
library SpreadCalculator {
    using SafeMath for uint256;

    // Constants for spread calculations
    uint256 public constant BASIS_POINTS = 10000;
    uint256 public constant MIN_SPREAD_BPS = 23; // 0.23% minimum spread
    uint256 public constant MAX_SPREAD_BPS = 1000; // 10% maximum spread (safety)
    uint256 public constant PRECISION = 1e18;
    
    // Fee structure
    uint256 public constant FLASH_LOAN_FEE_BPS = 9; // 0.09% Aave flash loan fee
    uint256 public constant GAS_BUFFER_BPS = 5; // 0.05% gas buffer
    uint256 public constant PROFIT_MARGIN_BPS = 9; // 0.09% minimum profit margin
    uint256 public constant TOTAL_COST_BPS = FLASH_LOAN_FEE_BPS + GAS_BUFFER_BPS + PROFIT_MARGIN_BPS; // 23bps total

    struct SpreadData {
        uint256 impliedPrice;
        uint256 externalPrice;
        int256 spreadBps;
        uint256 absoluteSpread;
        bool isProfitable;
        uint256 estimatedProfit;
        uint256 priceImpact;
        uint256 timestamp;
    }

    struct ArbitrageOpportunity {
        address tokenA;
        address tokenB;
        uint256 amountIn;
        uint256 expectedOut;
        int256 spreadBps;
        uint256 estimatedProfit;
        uint256 gasEstimate;
        bool isValid;
        string dexPath;
        uint256 deadline;
    }

    /**
     * @dev Calculate spread between implied and external price
     * Formula: spreadBps = (impliedPrice - externalPrice) / externalPrice * 10000
     * @param impliedPrice Price from DEX (Balancer/Curve)
     * @param externalPrice Reference price (Chainlink/0x API)
     * @return spreadBps Spread in basis points (positive = implied > external)
     */
    function calculateSpreadBps(
        uint256 impliedPrice,
        uint256 externalPrice
    ) internal pure returns (int256 spreadBps) {
        require(externalPrice > 0, "SpreadCalculator: ZERO_EXTERNAL_PRICE");
        require(impliedPrice > 0, "SpreadCalculator: ZERO_IMPLIED_PRICE");
        
        if (impliedPrice >= externalPrice) {
            spreadBps = int256(impliedPrice.sub(externalPrice).mul(BASIS_POINTS).div(externalPrice));
        } else {
            spreadBps = -int256(externalPrice.sub(impliedPrice).mul(BASIS_POINTS).div(externalPrice));
        }
    }

    /**
     * @dev Check if spread meets minimum 23bps threshold
     * @param spreadBps Spread in basis points
     * @return isProfitable True if spread exceeds minimum threshold
     */
    function isProfitableSpread(int256 spreadBps) internal pure returns (bool isProfitable) {
        uint256 absoluteSpread = spreadBps >= 0 ? uint256(spreadBps) : uint256(-spreadBps);
        return absoluteSpread >= MIN_SPREAD_BPS;
    }

    /**
     * @dev Calculate estimated profit after all fees
     * @param amount Trade amount
     * @param spreadBps Spread in basis points
     * @param gasEstimateUSD Gas cost estimate in USD
     * @return netProfit Net profit after fees and gas
     * @return grossProfit Gross profit before fees
     */
    function calculateProfit(
        uint256 amount,
        int256 spreadBps,
        uint256 gasEstimateUSD
    ) internal pure returns (uint256 netProfit, uint256 grossProfit) {
        require(amount > 0, "SpreadCalculator: ZERO_AMOUNT");
        
        uint256 absoluteSpread = spreadBps >= 0 ? uint256(spreadBps) : uint256(-spreadBps);
        
        // Calculate gross profit
        grossProfit = amount.mul(absoluteSpread).div(BASIS_POINTS);
        
        // Subtract fees and costs
        uint256 totalCosts = amount.mul(TOTAL_COST_BPS).div(BASIS_POINTS).add(gasEstimateUSD);
        
        if (grossProfit > totalCosts) {
            netProfit = grossProfit.sub(totalCosts);
        } else {
            netProfit = 0;
        }
    }

    /**
     * @dev Analyze arbitrage opportunity with comprehensive checks
     * @param impliedPrice DEX implied price
     * @param externalPrice External reference price
     * @param amount Trade amount
     * @param gasEstimateUSD Gas cost estimate
     * @param priceImpact Expected price impact
     * @return opportunity Complete arbitrage opportunity data
     */
    function analyzeOpportunity(
        uint256 impliedPrice,
        uint256 externalPrice,
        uint256 amount,
        uint256 gasEstimateUSD,
        uint256 priceImpact
    ) internal view returns (ArbitrageOpportunity memory opportunity) {
        int256 spreadBps = calculateSpreadBps(impliedPrice, externalPrice);
        (uint256 netProfit, ) = calculateProfit(amount, spreadBps, gasEstimateUSD);
        
        opportunity = ArbitrageOpportunity({
            tokenA: address(0), // To be set by caller
            tokenB: address(0), // To be set by caller
            amountIn: amount,
            expectedOut: 0, // To be calculated by caller
            spreadBps: spreadBps,
            estimatedProfit: netProfit,
            gasEstimate: gasEstimateUSD,
            isValid: _validateOpportunity(spreadBps, netProfit, priceImpact),
            dexPath: "", // To be set by caller
            deadline: block.timestamp + 300 // 5 minutes
        });
    }

    /**
     * @dev Calculate triangular arbitrage profit for A→B→C→A path
     * @param priceAB Price of A in terms of B
     * @param priceBC Price of B in terms of C  
     * @param priceCA Price of C in terms of A
     * @param amount Starting amount of token A
     * @return profit Net profit in token A
     * @return isArbitrage True if triangular arbitrage exists
     */
    function calculateTriangularArbitrage(
        uint256 priceAB,
        uint256 priceBC,
        uint256 priceCA,
        uint256 amount
    ) internal pure returns (uint256 profit, bool isArbitrage) {
        require(priceAB > 0 && priceBC > 0 && priceCA > 0, "SpreadCalculator: ZERO_PRICE");
        
        // Calculate final amount after A→B→C→A
        uint256 amountB = amount.mul(priceAB).div(PRECISION);
        uint256 amountC = amountB.mul(priceBC).div(PRECISION);
        uint256 finalAmountA = amountC.mul(priceCA).div(PRECISION);
        
        if (finalAmountA > amount) {
            profit = finalAmountA.sub(amount);
            
            // Check if profit exceeds minimum threshold
            uint256 profitBps = profit.mul(BASIS_POINTS).div(amount);
            isArbitrage = profitBps >= MIN_SPREAD_BPS;
        } else {
            profit = 0;
            isArbitrage = false;
        }
    }

    /**
     * @dev Calculate optimal trade size for maximum profit
     * Uses simplified model: profit = spread * amount - impact * amount^2
     * @param spreadBps Spread in basis points
     * @param priceImpactFactor Price impact factor
     * @param maxAmount Maximum trade amount
     * @return optimalAmount Optimal trade amount
     */
    function calculateOptimalSize(
        uint256 spreadBps,
        uint256 priceImpactFactor,
        uint256 maxAmount
    ) internal pure returns (uint256 optimalAmount) {
        if (priceImpactFactor == 0) {
            return maxAmount;
        }
        
        // Optimal size = spread / (2 * impact_factor)
        optimalAmount = spreadBps.mul(PRECISION).div(priceImpactFactor.mul(2));
        
        if (optimalAmount > maxAmount) {
            optimalAmount = maxAmount;
        }
    }

    /**
     * @dev Monitor spread over time for trend analysis
     * @param currentSpread Current spread value
     * @param previousSpread Previous spread value
     * @param timeElapsed Time elapsed between measurements
     * @return trend Spread trend (positive = increasing, negative = decreasing)
     * @return velocity Rate of change in bps per second
     */
    function analyzeTrend(
        int256 currentSpread,
        int256 previousSpread,
        uint256 timeElapsed
    ) internal pure returns (int256 trend, int256 velocity) {
        require(timeElapsed > 0, "SpreadCalculator: ZERO_TIME");
        
        trend = currentSpread - previousSpread;
        velocity = trend / int256(timeElapsed);
    }

    /**
     * @dev Validate arbitrage opportunity against all criteria
     * @param spreadBps Spread in basis points
     * @param netProfit Net profit estimate
     * @param priceImpact Price impact estimate
     * @return isValid True if opportunity meets all criteria
     */
    function _validateOpportunity(
        int256 spreadBps,
        uint256 netProfit,
        uint256 priceImpact
    ) private pure returns (bool isValid) {
        uint256 absoluteSpread = spreadBps >= 0 ? uint256(spreadBps) : uint256(-spreadBps);
        
        return (
            absoluteSpread >= MIN_SPREAD_BPS && // Minimum spread threshold
            absoluteSpread <= MAX_SPREAD_BPS && // Maximum spread safety check
            netProfit > 0 && // Must be profitable after fees
            priceImpact <= 500 // Max 5% price impact
        );
    }

    /**
     * @dev Create spread monitoring data structure
     * @param impliedPrice DEX implied price
     * @param externalPrice External reference price
     * @param priceImpact Price impact estimate
     * @return spreadData Complete spread analysis
     */
    function createSpreadData(
        uint256 impliedPrice,
        uint256 externalPrice,
        uint256 priceImpact
    ) internal view returns (SpreadData memory spreadData) {
        int256 spreadBps = calculateSpreadBps(impliedPrice, externalPrice);
        uint256 absoluteSpread = spreadBps >= 0 ? uint256(spreadBps) : uint256(-spreadBps);
        
        spreadData = SpreadData({
            impliedPrice: impliedPrice,
            externalPrice: externalPrice,
            spreadBps: spreadBps,
            absoluteSpread: absoluteSpread,
            isProfitable: isProfitableSpread(spreadBps),
            estimatedProfit: 0, // To be calculated with amount
            priceImpact: priceImpact,
            timestamp: block.timestamp
        });
    }

    /**
     * @dev Emergency circuit breaker for extreme spreads
     * @param spreadBps Current spread
     * @return shouldHalt True if trading should be halted
     */
    function checkCircuitBreaker(int256 spreadBps) internal pure returns (bool shouldHalt) {
        uint256 absoluteSpread = spreadBps >= 0 ? uint256(spreadBps) : uint256(-spreadBps);
        return absoluteSpread > MAX_SPREAD_BPS;
    }
}

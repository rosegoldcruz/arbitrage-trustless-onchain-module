// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@chainlink/contracts/src/v0.8/shared/interfaces/AggregatorV3Interface.sol";

/**
 * @title AEONArbitrageExtensions
 * @dev Complete arbitrage math library with Balancer, Curve, and 23bps threshold logic
 */

interface ICurvePool {
    function get_virtual_price() external view returns (uint256);
    function exchange(int128 i, int128 j, uint256 dx, uint256 min_dy) external returns (uint256);
    function get_dy(int128 i, int128 j, uint256 dx) external view returns (uint256);
    function balances(uint256 i) external view returns (uint256);
    function A() external view returns (uint256);
}

interface IBalancerVault {
    function getPoolTokens(bytes32 poolId) external view returns (
        address[] memory tokens,
        uint256[] memory balances,
        uint256 lastChangeBlock
    );
}

interface IBalancerPool {
    function getPoolId() external view returns (bytes32);
    function getNormalizedWeights() external view returns (uint256[] memory);
    function getSwapFeePercentage() external view returns (uint256);
}

library AEONMath {
    using SafeMath for uint256;
    
    uint256 private constant ONE = 1e18;
    uint256 private constant BASIS_POINTS = 10000;
    uint256 private constant MIN_SPREAD_BPS = 23; // 0.23% minimum threshold
    
    /**
     * @dev Calculate Balancer weighted pool implied price
     * Formula: P = (balanceIn * weightOut) / (balanceOut * weightIn)
     * @param balanceIn Balance of input token
     * @param balanceOut Balance of output token  
     * @param weightIn Weight of input token (normalized)
     * @param weightOut Weight of output token (normalized)
     * @return impliedPrice Implied price in 18 decimals
     */
    function getBalancerImpliedPrice(
        uint256 balanceIn,
        uint256 balanceOut,
        uint256 weightIn,
        uint256 weightOut
    ) internal pure returns (uint256 impliedPrice) {
        require(balanceOut > 0 && weightIn > 0, "AEONMath: INVALID_BALANCES");
        return (balanceIn.mul(weightOut)).div(balanceOut.mul(weightIn));
    }
    
    /**
     * @dev Calculate Balancer swap output with fees
     * Supports asymmetric weights (80/20, 98/2)
     * @param balanceIn Input token balance
     * @param balanceOut Output token balance
     * @param weightIn Input token weight
     * @param weightOut Output token weight
     * @param amountIn Input amount
     * @param swapFee Swap fee percentage (e.g., 0.003 for 0.3%)
     * @return amountOut Output amount after fees
     */
    function calcBalancerOutGivenIn(
        uint256 balanceIn,
        uint256 balanceOut,
        uint256 weightIn,
        uint256 weightOut,
        uint256 amountIn,
        uint256 swapFee
    ) internal pure returns (uint256 amountOut) {
        require(amountIn <= balanceIn.div(2), "AEONMath: MAX_IN_RATIO");
        
        uint256 normalizedWeight = weightIn.mul(ONE).div(weightOut);
        uint256 adjustedIn = amountIn.mul(ONE.sub(swapFee)).div(ONE);
        uint256 y = balanceIn.mul(ONE).div(balanceIn.add(adjustedIn));
        uint256 foo = _pow(y, normalizedWeight);
        uint256 bar = ONE.sub(foo);
        amountOut = balanceOut.mul(bar).div(ONE);
        
        require(amountOut <= balanceOut.div(3), "AEONMath: MAX_OUT_RATIO");
    }
    
    /**
     * @dev Get Curve StableSwap virtual price for depeg detection
     * @param pool Curve pool address
     * @return virtualPrice Virtual price from pool
     */
    function getCurveVirtualPrice(address pool) internal view returns (uint256) {
        return ICurvePool(pool).get_virtual_price();
    }
    
    /**
     * @dev Calculate Curve StableSwap output amount
     * @param pool Curve pool address
     * @param i Input token index
     * @param j Output token index  
     * @param dx Input amount
     * @return dy Output amount
     */
    function getCurveOutputAmount(
        address pool,
        int128 i,
        int128 j,
        uint256 dx
    ) internal view returns (uint256 dy) {
        return ICurvePool(pool).get_dy(i, j, dx);
    }
    
    /**
     * @dev Detect Curve pool depeg condition
     * @param pool Curve pool address
     * @param expectedPrice Expected price (1e18 for 1:1)
     * @param threshold Depeg threshold (e.g., 0.02e18 for 2%)
     * @return isDepegged True if pool is depegged
     */
    function detectCurveDepeg(
        address pool,
        uint256 expectedPrice,
        uint256 threshold
    ) internal view returns (bool isDepegged) {
        uint256 virtualPrice = getCurveVirtualPrice(pool);
        uint256 deviation = virtualPrice > expectedPrice 
            ? virtualPrice.sub(expectedPrice)
            : expectedPrice.sub(virtualPrice);
        
        return deviation.mul(ONE).div(expectedPrice) > threshold;
    }
    
    /**
     * @dev Calculate spread in basis points
     * Formula: spreadBps = ((impliedPrice - externalPrice) / externalPrice) * 10000
     * @param impliedPrice DEX implied price
     * @param externalPrice External oracle price
     * @return spreadBps Spread in basis points (can be negative)
     */
    function calculateSpreadBps(
        uint256 impliedPrice,
        uint256 externalPrice
    ) internal pure returns (int256 spreadBps) {
        require(externalPrice > 0, "AEONMath: INVALID_EXTERNAL_PRICE");
        
        if (impliedPrice >= externalPrice) {
            spreadBps = int256(impliedPrice.sub(externalPrice).mul(BASIS_POINTS).div(externalPrice));
        } else {
            spreadBps = -int256(externalPrice.sub(impliedPrice).mul(BASIS_POINTS).div(externalPrice));
        }
    }
    
    /**
     * @dev Check if spread exceeds 23bps threshold
     * @param spreadBps Spread in basis points
     * @param totalFeesBps Total fees in basis points (gas + DEX fees)
     * @return isAboveThreshold True if profitable after fees
     */
    function isAboveThreshold(
        int256 spreadBps,
        uint256 totalFeesBps
    ) internal pure returns (bool) {
        uint256 absoluteSpread = spreadBps >= 0 ? uint256(spreadBps) : uint256(-spreadBps);
        return absoluteSpread > totalFeesBps.add(MIN_SPREAD_BPS);
    }
    
    /**
     * @dev Calculate triangular arbitrage profit
     * @param priceAB A→B price
     * @param priceBC B→C price  
     * @param priceCA C→A price
     * @param amount Input amount
     * @return profit Net profit amount
     * @return isProfitable True if profitable
     */
    function calculateTriangularProfit(
        uint256 priceAB,
        uint256 priceBC,
        uint256 priceCA,
        uint256 amount
    ) internal pure returns (uint256 profit, bool isProfitable) {
        // Calculate final amount after A→B→C→A
        uint256 amountB = amount.mul(priceAB).div(ONE);
        uint256 amountC = amountB.mul(priceBC).div(ONE);
        uint256 finalAmountA = amountC.mul(priceCA).div(ONE);
        
        if (finalAmountA > amount) {
            profit = finalAmountA.sub(amount);
            uint256 profitBps = profit.mul(BASIS_POINTS).div(amount);
            isProfitable = profitBps >= MIN_SPREAD_BPS;
        } else {
            profit = 0;
            isProfitable = false;
        }
    }
    
    /**
     * @dev Simplified power function for Balancer math
     * @param base Base value (18 decimals)
     * @param exp Exponent value (18 decimals)
     * @return result Base^exp (18 decimals)
     */
    function _pow(uint256 base, uint256 exp) private pure returns (uint256 result) {
        require(base >= ONE.div(10) && base <= 10 * ONE, "AEONMath: BASE_OUT_OF_BOUNDS");
        require(exp <= 2 * ONE, "AEONMath: EXP_OUT_OF_BOUNDS");

        if (exp == 0) return ONE;
        if (exp == ONE) return base;
        if (base == ONE) return ONE;

        // Taylor series approximation for gas efficiency
        uint256 x = base;
        uint256 n = exp;
        result = ONE;
        
        // Simple approximation: (1 + x)^n ≈ 1 + n*x for small x
        if (base > ONE) {
            uint256 excess = base.sub(ONE);
            result = ONE.add(excess.mul(n).div(ONE));
        } else {
            uint256 deficit = ONE.sub(base);
            result = ONE.sub(deficit.mul(n).div(ONE));
        }
    }
}

/**
 * @title ChainlinkPriceOracle
 * @dev Chainlink price feed integration for Base Sepolia
 */
library ChainlinkPriceOracle {
    
    // Base Sepolia Chainlink Price Feeds
    address constant ETH_USD_FEED = 0xd276FCf34D54A9267738E680a72b7Eaf2E54f2e4;
    address constant DAI_USD_FEED = 0x591e79239a7d679378eC8c847e5038150364C78F;
    address constant USDC_USD_FEED = 0xd30e2101a97dcbAeBCBC04F14C3f624E67A35165;
    
    uint256 constant PRICE_STALENESS_THRESHOLD = 3600; // 1 hour
    
    /**
     * @dev Get latest price from Chainlink feed
     * @param priceFeed Chainlink price feed address
     * @return price Latest price (8 decimals)
     * @return isStale True if price is stale
     */
    function getLatestPrice(address priceFeed) internal view returns (uint256 price, bool isStale) {
        AggregatorV3Interface feed = AggregatorV3Interface(priceFeed);
        
        try feed.latestRoundData() returns (
            uint80 roundId,
            int256 answer,
            uint256 startedAt,
            uint256 updatedAt,
            uint80 answeredInRound
        ) {
            require(answer > 0, "ChainlinkOracle: INVALID_PRICE");
            price = uint256(answer);
            isStale = (block.timestamp - updatedAt) > PRICE_STALENESS_THRESHOLD;
        } catch {
            price = 0;
            isStale = true;
        }
    }
    
    /**
     * @dev Get ETH/USD price from Base Sepolia feed
     * @return price ETH price in USD (8 decimals)
     * @return isStale True if price is stale
     */
    function getETHPrice() internal view returns (uint256 price, bool isStale) {
        return getLatestPrice(ETH_USD_FEED);
    }
    
    /**
     * @dev Get DAI/USD price from Base Sepolia feed
     * @return price DAI price in USD (8 decimals)
     * @return isStale True if price is stale
     */
    function getDAIPrice() internal view returns (uint256 price, bool isStale) {
        return getLatestPrice(DAI_USD_FEED);
    }
    
    /**
     * @dev Get USDC/USD price from Base Sepolia feed
     * @return price USDC price in USD (8 decimals)
     * @return isStale True if price is stale
     */
    function getUSDCPrice() internal view returns (uint256 price, bool isStale) {
        return getLatestPrice(USDC_USD_FEED);
    }

    /**
     * @dev Check if slippage is acceptable
     * @param actualSlippageBps Actual slippage in basis points
     * @param maxSlippageBps Maximum allowed slippage in basis points
     * @return acceptable True if slippage is within limits
     */
    function isSlippageAcceptable(uint256 actualSlippageBps, uint256 maxSlippageBps)
        internal
        pure
        returns (bool acceptable)
    {
        return actualSlippageBps <= maxSlippageBps;
    }

    /**
     * @dev Calculate efficiency score for arbitrage opportunity
     * @param expectedProfitUSD Expected profit in USD
     * @param gasUsed Estimated gas usage
     * @param gasPriceWei Gas price in wei
     * @return score Efficiency score (higher is better)
     */
    function efficiencyScore(
        uint256 expectedProfitUSD,
        uint256 gasUsed,
        uint256 gasPriceWei
    ) internal pure returns (int256 score) {
        uint256 gasCostWei = gasUsed * gasPriceWei;
        // Convert gas cost to USD (simplified - would need ETH/USD price in real implementation)
        uint256 gasCostUSD = (gasCostWei / 1e18) * 2000; // Assume $2000 ETH

        if (expectedProfitUSD > gasCostUSD) {
            return int256(expectedProfitUSD - gasCostUSD);
        } else {
            return -int256(gasCostUSD - expectedProfitUSD);
        }
    }

    /**
     * @dev Calculate spread in basis points between two prices
     * @param impliedPrice Implied price from DEX
     * @param externalPrice External reference price
     * @return spreadBps Spread in basis points (can be negative)
     */
    function calculateSpreadBps(uint256 impliedPrice, uint256 externalPrice)
        internal
        pure
        returns (int256 spreadBps)
    {
        require(externalPrice > 0, "AEONMath: INVALID_EXTERNAL_PRICE");

        if (impliedPrice > externalPrice) {
            uint256 diff = impliedPrice - externalPrice;
            return int256((diff * 10000) / externalPrice);
        } else {
            uint256 diff = externalPrice - impliedPrice;
            return -int256((diff * 10000) / externalPrice);
        }
    }

    /**
     * @dev Check if spread is above minimum threshold
     * @param spreadBps Spread in basis points
     * @param thresholdBps Minimum threshold in basis points
     * @return isAbove True if spread exceeds threshold
     */
    function isAboveThreshold(int256 spreadBps, uint256 thresholdBps)
        internal
        pure
        returns (bool isAbove)
    {
        uint256 absSpread = uint256(spreadBps > 0 ? spreadBps : -spreadBps);
        return absSpread >= thresholdBps;
    }
}

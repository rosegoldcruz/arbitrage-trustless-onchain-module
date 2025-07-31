// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface ICurvePool {
    function get_virtual_price() external view returns (uint256);
}

library AEONMathStandalone {
    /// @notice Calculates implied price from Balancer-style weighted pools
    function getBalancerImpliedPrice(
        uint256 balanceIn,
        uint256 balanceOut,
        uint256 weightIn,
        uint256 weightOut
    ) internal pure returns (uint256 impliedPrice) {
        require(balanceOut > 0 && weightOut > 0, "Invalid output pool state");
        return (balanceIn * weightOut) / (balanceOut * weightIn);
    }

    /// @notice Fetches Curve StableSwap virtual price
    function getCurveVirtualPrice(address pool) internal view returns (uint256) {
        return ICurvePool(pool).get_virtual_price();
    }

    /// @notice Calculates spread in basis points between on-chain implied and off-chain oracle
    function calculateSpreadBps(
        uint256 impliedPrice,
        uint256 externalPrice
    ) internal pure returns (int256 spreadBps) {
        return int256((impliedPrice - externalPrice) * 10000 / externalPrice);
    }

    /// @notice Compares spread to total fees (e.g. slippage + gas + LP)
    function isAboveThreshold(
        int256 spreadBps,
        uint256 totalFeesBps
    ) internal pure returns (bool) {
        return spreadBps > int256(totalFeesBps);
    }

    /// @notice Calculates gas efficiency factor (for future use)
    function efficiencyScore(
        uint256 expectedProfitUSD,
        uint256 gasUsed,
        uint256 gasPriceWei
    ) internal pure returns (int256 score) {
        uint256 costUSD = (gasUsed * gasPriceWei) / 1e18; // assuming 1 ETH = 1 USD
        if (costUSD == 0) return int256(expectedProfitUSD * 1e18);
        return int256((expectedProfitUSD * 1e18) / costUSD); // higher is better
    }

    // --- SLIPPAGE THRESHOLD CHECK ---
    function isSlippageAcceptable(
        uint256 slippageBps,
        uint256 maxAllowedBps
    ) internal pure returns (bool) {
        return slippageBps <= maxAllowedBps;
    }

    // --- TRIANGULAR ARBITRAGE PROFIT CALCULATION ---
    function calculateTriangularProfit(
        uint256 priceAB,
        uint256 priceBC,
        uint256 priceCA,
        uint256 amountIn
    ) internal pure returns (uint256 profit, bool hasArbitrage) {
        // Calculate final amount after A→B→C→A cycle
        uint256 amountB = (amountIn * priceAB) / 1e18;
        uint256 amountC = (amountB * priceBC) / 1e18;
        uint256 finalAmountA = (amountC * priceCA) / 1e18;

        if (finalAmountA > amountIn) {
            profit = finalAmountA - amountIn;
            hasArbitrage = true;
        } else {
            profit = 0;
            hasArbitrage = false;
        }
    }

    // --- CURVE DEPEG DETECTION ---
    function detectCurveDepeg(
        address pool,
        uint256 expectedPrice,
        uint256 depegThreshold
    ) internal view returns (bool isDepegged) {
        try ICurvePool(pool).get_virtual_price() returns (uint256 virtualPrice) {
            uint256 priceDiff = virtualPrice > expectedPrice
                ? virtualPrice - expectedPrice
                : expectedPrice - virtualPrice;

            // Check if price deviation exceeds threshold
            isDepegged = (priceDiff * 1e18) / expectedPrice > depegThreshold;
        } catch {
            // If we can't get virtual price, assume depegged for safety
            isDepegged = true;
        }
    }
}

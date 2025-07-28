// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/utils/math/SafeMath.sol";

/**
 * @title BalancerMath
 * @dev Advanced Balancer weighted pool mathematics for arbitrage calculations
 * Supports asymmetric weights (80/20, 98/2) and implied price calculations
 */
library BalancerMath {
    using SafeMath for uint256;

    uint256 private constant ONE = 1e18;
    uint256 private constant MAX_WEIGHT = 50e18; // 50%
    uint256 private constant MIN_WEIGHT = 1e16;  // 1%
    uint256 private constant EXIT_FEE = 0;       // No exit fee for calculations
    uint256 private constant MAX_IN_RATIO = ONE / 2;  // 50%
    uint256 private constant MAX_OUT_RATIO = ONE / 3; // 33.33%

    /**
     * @dev Calculate spot price for Balancer weighted pool
     * Formula: spotPrice = (balanceIn / weightIn) / (balanceOut / weightOut)
     * @param balanceIn Token in balance
     * @param weightIn Token in weight (normalized)
     * @param balanceOut Token out balance  
     * @param weightOut Token out weight (normalized)
     * @return Spot price in 18 decimal precision
     */
    function calcSpotPrice(
        uint256 balanceIn,
        uint256 weightIn,
        uint256 balanceOut,
        uint256 weightOut
    ) internal pure returns (uint256) {
        require(balanceIn > 0 && balanceOut > 0, "BalancerMath: ZERO_BALANCE");
        require(weightIn >= MIN_WEIGHT && weightIn <= MAX_WEIGHT, "BalancerMath: INVALID_WEIGHT_IN");
        require(weightOut >= MIN_WEIGHT && weightOut <= MAX_WEIGHT, "BalancerMath: INVALID_WEIGHT_OUT");

        uint256 numer = balanceIn.mul(ONE).div(weightIn);
        uint256 denom = balanceOut.mul(ONE).div(weightOut);
        
        return numer.mul(ONE).div(denom);
    }

    /**
     * @dev Calculate implied price from Balancer pool state
     * Used for arbitrage spread calculations against external prices
     * @param balanceIn Token in balance
     * @param balanceOut Token out balance
     * @param weightIn Token in weight (e.g., 0.8e18 for 80%)
     * @param weightOut Token out weight (e.g., 0.2e18 for 20%)
     * @return Implied price in 18 decimal precision
     */
    function getImpliedPrice(
        uint256 balanceIn,
        uint256 balanceOut,
        uint256 weightIn,
        uint256 weightOut
    ) internal pure returns (uint256) {
        return calcSpotPrice(balanceIn, weightIn, balanceOut, weightOut);
    }

    /**
     * @dev Calculate output amount for exact input (swapExactAmountIn)
     * Formula: tokenAmountOut = balanceOut * (1 - (balanceIn / (balanceIn + tokenAmountIn))^(weightIn/weightOut))
     * @param tokenBalanceIn Current balance of token in
     * @param tokenWeightIn Weight of token in
     * @param tokenBalanceOut Current balance of token out
     * @param tokenWeightOut Weight of token out
     * @param tokenAmountIn Amount of token in
     * @param swapFee Swap fee (e.g., 0.003e18 for 0.3%)
     * @return tokenAmountOut Amount of token out
     */
    function calcOutGivenIn(
        uint256 tokenBalanceIn,
        uint256 tokenWeightIn,
        uint256 tokenBalanceOut,
        uint256 tokenWeightOut,
        uint256 tokenAmountIn,
        uint256 swapFee
    ) internal pure returns (uint256 tokenAmountOut) {
        require(tokenAmountIn <= tokenBalanceIn.mul(MAX_IN_RATIO).div(ONE), "BalancerMath: MAX_IN_RATIO");
        
        uint256 normalizedWeight = tokenWeightIn.mul(ONE).div(tokenWeightOut);
        uint256 adjustedIn = tokenAmountIn.mul(ONE.sub(swapFee)).div(ONE);
        uint256 y = tokenBalanceIn.mul(ONE).div(tokenBalanceIn.add(adjustedIn));
        uint256 foo = _pow(y, normalizedWeight);
        uint256 bar = ONE.sub(foo);
        tokenAmountOut = tokenBalanceOut.mul(bar).div(ONE);
        
        require(tokenAmountOut <= tokenBalanceOut.mul(MAX_OUT_RATIO).div(ONE), "BalancerMath: MAX_OUT_RATIO");
    }

    /**
     * @dev Calculate input amount for exact output (swapExactAmountOut)
     * Formula: tokenAmountIn = balanceIn * ((balanceOut / (balanceOut - tokenAmountOut))^(weightOut/weightIn) - 1)
     * @param tokenBalanceIn Current balance of token in
     * @param tokenWeightIn Weight of token in
     * @param tokenBalanceOut Current balance of token out
     * @param tokenWeightOut Weight of token out
     * @param tokenAmountOut Desired amount of token out
     * @param swapFee Swap fee
     * @return tokenAmountIn Required amount of token in
     */
    function calcInGivenOut(
        uint256 tokenBalanceIn,
        uint256 tokenWeightIn,
        uint256 tokenBalanceOut,
        uint256 tokenWeightOut,
        uint256 tokenAmountOut,
        uint256 swapFee
    ) internal pure returns (uint256 tokenAmountIn) {
        require(tokenAmountOut <= tokenBalanceOut.mul(MAX_OUT_RATIO).div(ONE), "BalancerMath: MAX_OUT_RATIO");
        
        uint256 normalizedWeight = tokenWeightOut.mul(ONE).div(tokenWeightIn);
        uint256 y = tokenBalanceOut.mul(ONE).div(tokenBalanceOut.sub(tokenAmountOut));
        uint256 foo = _pow(y, normalizedWeight);
        uint256 tokenAmountInBeforeFee = tokenBalanceIn.mul(foo.sub(ONE)).div(ONE);
        tokenAmountIn = tokenAmountInBeforeFee.mul(ONE).div(ONE.sub(swapFee));
        
        require(tokenAmountIn <= tokenBalanceIn.mul(MAX_IN_RATIO).div(ONE), "BalancerMath: MAX_IN_RATIO");
    }

    /**
     * @dev Calculate price impact for a given trade
     * @param balanceIn Token in balance
     * @param balanceOut Token out balance
     * @param weightIn Token in weight
     * @param weightOut Token out weight
     * @param amountIn Amount being traded
     * @return priceImpact Price impact in basis points (10000 = 100%)
     */
    function calcPriceImpact(
        uint256 balanceIn,
        uint256 balanceOut,
        uint256 weightIn,
        uint256 weightOut,
        uint256 amountIn
    ) internal pure returns (uint256 priceImpact) {
        uint256 spotPriceBefore = calcSpotPrice(balanceIn, weightIn, balanceOut, weightOut);
        uint256 newBalanceIn = balanceIn.add(amountIn);
        uint256 spotPriceAfter = calcSpotPrice(newBalanceIn, weightIn, balanceOut, weightOut);
        
        if (spotPriceAfter > spotPriceBefore) {
            priceImpact = spotPriceAfter.sub(spotPriceBefore).mul(10000).div(spotPriceBefore);
        } else {
            priceImpact = 0;
        }
    }

    /**
     * @dev Calculate arbitrage profit potential between Balancer and external price
     * @param balancerPrice Current Balancer implied price
     * @param externalPrice External market price (from Chainlink/0x)
     * @param amount Trade amount
     * @return profit Potential profit in token units
     * @return spreadBps Spread in basis points
     */
    function calcArbitrageProfit(
        uint256 balancerPrice,
        uint256 externalPrice,
        uint256 amount
    ) internal pure returns (uint256 profit, int256 spreadBps) {
        spreadBps = int256(balancerPrice.sub(externalPrice).mul(10000).div(externalPrice));
        
        if (spreadBps > 0) {
            // Balancer price higher - buy external, sell on Balancer
            profit = amount.mul(uint256(spreadBps)).div(10000);
        } else {
            // External price higher - buy on Balancer, sell external
            profit = amount.mul(uint256(-spreadBps)).div(10000);
        }
    }

    /**
     * @dev Simplified power function for weight calculations
     * Uses Taylor series approximation for gas efficiency
     * @param base Base value (18 decimals)
     * @param exp Exponent value (18 decimals)
     * @return result Base^exp (18 decimals)
     */
    function _pow(uint256 base, uint256 exp) private pure returns (uint256 result) {
        require(base >= ONE / 10 && base <= 10 * ONE, "BalancerMath: BASE_OUT_OF_BOUNDS");
        require(exp >= 0 && exp <= 2 * ONE, "BalancerMath: EXP_OUT_OF_BOUNDS");

        if (exp == 0) return ONE;
        if (exp == ONE) return base;
        if (base == ONE) return ONE;

        // Use simplified approximation for gas efficiency
        // For production, consider using more sophisticated math libraries
        uint256 x = base;
        uint256 n = exp;
        result = ONE;

        while (n > 0) {
            if (n % 2 == 1) {
                result = result.mul(x).div(ONE);
            }
            x = x.mul(x).div(ONE);
            n = n.div(2);
        }
    }

    /**
     * @dev Validate pool parameters for arbitrage calculations
     * @param balanceIn Token in balance
     * @param balanceOut Token out balance
     * @param weightIn Token in weight
     * @param weightOut Token out weight
     * @return valid True if parameters are valid
     */
    function validatePoolParams(
        uint256 balanceIn,
        uint256 balanceOut,
        uint256 weightIn,
        uint256 weightOut
    ) internal pure returns (bool valid) {
        return (
            balanceIn > 0 &&
            balanceOut > 0 &&
            weightIn >= MIN_WEIGHT &&
            weightIn <= MAX_WEIGHT &&
            weightOut >= MIN_WEIGHT &&
            weightOut <= MAX_WEIGHT &&
            weightIn.add(weightOut) <= ONE
        );
    }
}

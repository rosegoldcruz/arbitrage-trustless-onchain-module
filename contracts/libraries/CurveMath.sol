// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/utils/math/SafeMath.sol";

/**
 * @title CurveMath
 * @dev Advanced Curve StableSwap invariant calculations for arbitrage
 * Includes virtual price calculations and depeg detection mechanisms
 */
library CurveMath {
    using SafeMath for uint256;

    uint256 private constant A_PRECISION = 100;
    uint256 private constant MAX_A = 10**6;
    uint256 private constant MAX_A_CHANGE = 10;
    uint256 private constant MIN_RAMP_TIME = 86400; // 1 day
    uint256 private constant PRECISION = 1e18;
    uint256 private constant FEE_DENOMINATOR = 10**10;
    uint256 private constant MAX_ADMIN_FEE = 10**10;
    uint256 private constant MAX_FEE = 5 * 10**9; // 0.5%
    uint256 private constant N_COINS = 3; // For DAI/USDC/GHO triangular arbitrage

    /**
     * @dev Calculate StableSwap invariant D
     * D = (A * S + D_P * N) / (A - 1 + N)
     * Where S = sum of balances, D_P = product term
     * @param A Amplification coefficient
     * @param balances Array of token balances
     * @return D Invariant value
     */
    function calculateD(uint256 A, uint256[] memory balances) 
        internal 
        pure 
        returns (uint256 D) 
    {
        require(balances.length >= 2, "CurveMath: INSUFFICIENT_COINS");
        
        uint256 S = 0;
        uint256 Dprev = 0;
        
        for (uint256 i = 0; i < balances.length; i++) {
            S = S.add(balances[i]);
        }
        
        if (S == 0) return 0;
        
        D = S;
        uint256 Ann = A.mul(balances.length);
        
        // Newton's method iteration
        for (uint256 i = 0; i < 255; i++) {
            uint256 D_P = D;
            
            for (uint256 j = 0; j < balances.length; j++) {
                D_P = D_P.mul(D).div(balances[j].mul(balances.length));
            }
            
            Dprev = D;
            D = Ann.mul(S).add(D_P.mul(balances.length)).mul(D).div(
                Ann.sub(1).mul(D).add(balances.length.add(1).mul(D_P))
            );
            
            // Convergence check
            if (D > Dprev) {
                if (D.sub(Dprev) <= 1) break;
            } else {
                if (Dprev.sub(D) <= 1) break;
            }
        }
    }

    /**
     * @dev Calculate virtual price for Curve pool
     * Virtual price = D / (sum of balances)
     * Used for depeg detection and arbitrage opportunities
     * @param A Amplification coefficient
     * @param balances Array of token balances
     * @param totalSupply Total LP token supply
     * @return virtualPrice Virtual price in 18 decimals
     */
    function getVirtualPrice(
        uint256 A,
        uint256[] memory balances,
        uint256 totalSupply
    ) internal pure returns (uint256 virtualPrice) {
        if (totalSupply == 0) return PRECISION;
        
        uint256 D = calculateD(A, balances);
        return D.mul(PRECISION).div(totalSupply);
    }

    /**
     * @dev Calculate output amount for StableSwap
     * @param A Amplification coefficient
     * @param i Index of input token
     * @param j Index of output token
     * @param dx Input amount
     * @param balances Current balances
     * @param fee Swap fee (in FEE_DENOMINATOR units)
     * @return dy Output amount after fees
     */
    function getDy(
        uint256 A,
        uint256 i,
        uint256 j,
        uint256 dx,
        uint256[] memory balances,
        uint256 fee
    ) internal pure returns (uint256 dy) {
        require(i != j, "CurveMath: SAME_COIN");
        require(i < balances.length && j < balances.length, "CurveMath: COIN_NOT_FOUND");
        
        uint256 D = calculateD(A, balances);
        uint256[] memory newBalances = new uint256[](balances.length);
        
        for (uint256 k = 0; k < balances.length; k++) {
            newBalances[k] = balances[k];
        }
        
        newBalances[i] = newBalances[i].add(dx);
        uint256 y = getY(A, j, newBalances, D);
        dy = balances[j].sub(y).sub(1); // -1 for rounding
        
        // Apply fee
        uint256 feeAmount = dy.mul(fee).div(FEE_DENOMINATOR);
        dy = dy.sub(feeAmount);
    }

    /**
     * @dev Calculate required input amount for desired output
     * @param A Amplification coefficient
     * @param i Index of input token
     * @param j Index of output token
     * @param dy Desired output amount
     * @param balances Current balances
     * @param fee Swap fee
     * @return dx Required input amount
     */
    function getDx(
        uint256 A,
        uint256 i,
        uint256 j,
        uint256 dy,
        uint256[] memory balances,
        uint256 fee
    ) internal pure returns (uint256 dx) {
        require(i != j, "CurveMath: SAME_COIN");
        require(i < balances.length && j < balances.length, "CurveMath: COIN_NOT_FOUND");
        
        // Account for fee in desired output
        uint256 dyWithFee = dy.mul(FEE_DENOMINATOR).div(FEE_DENOMINATOR.sub(fee));
        
        uint256 D = calculateD(A, balances);
        uint256[] memory newBalances = new uint256[](balances.length);
        
        for (uint256 k = 0; k < balances.length; k++) {
            newBalances[k] = balances[k];
        }
        
        newBalances[j] = balances[j].sub(dyWithFee);
        uint256 x = getY(A, i, newBalances, D);
        dx = x.sub(balances[i]).add(1); // +1 for rounding
    }

    /**
     * @dev Calculate Y given other balances and invariant D
     * Solves: A * n^n * S + D = A * D * n^n + D^(n+1) / (n^n * prod)
     * @param A Amplification coefficient
     * @param i Index of token to calculate
     * @param balances Array of balances (with target balance set to 0)
     * @param D Invariant
     * @return y Balance of token i
     */
    function getY(
        uint256 A,
        uint256 i,
        uint256[] memory balances,
        uint256 D
    ) internal pure returns (uint256 y) {
        require(i < balances.length, "CurveMath: COIN_NOT_FOUND");
        
        uint256 c = D;
        uint256 S = 0;
        uint256 Ann = A.mul(balances.length);
        
        for (uint256 j = 0; j < balances.length; j++) {
            if (j != i) {
                S = S.add(balances[j]);
                c = c.mul(D).div(balances[j].mul(balances.length));
            }
        }
        
        c = c.mul(D).div(Ann.mul(balances.length));
        uint256 b = S.add(D.div(Ann));
        
        uint256 yPrev = 0;
        y = D;
        
        // Newton's method
        for (uint256 k = 0; k < 255; k++) {
            yPrev = y;
            y = y.mul(y).add(c).div(y.mul(2).add(b).sub(D));
            
            if (y > yPrev) {
                if (y.sub(yPrev) <= 1) break;
            } else {
                if (yPrev.sub(y) <= 1) break;
            }
        }
    }

    /**
     * @dev Detect depeg condition in stablecoin pool
     * @param balances Array of token balances
     * @param expectedRatio Expected ratio (1e18 for 1:1:1)
     * @param depegThreshold Threshold for depeg detection (e.g., 0.02e18 for 2%)
     * @return isDepegged True if any token is depegged
     * @return maxDeviation Maximum deviation from expected ratio
     */
    function detectDepeg(
        uint256[] memory balances,
        uint256 expectedRatio,
        uint256 depegThreshold
    ) internal pure returns (bool isDepegged, uint256 maxDeviation) {
        require(balances.length >= 2, "CurveMath: INSUFFICIENT_COINS");
        
        uint256 totalBalance = 0;
        for (uint256 i = 0; i < balances.length; i++) {
            totalBalance = totalBalance.add(balances[i]);
        }
        
        uint256 expectedBalance = totalBalance.div(balances.length);
        maxDeviation = 0;
        
        for (uint256 i = 0; i < balances.length; i++) {
            uint256 deviation;
            if (balances[i] > expectedBalance) {
                deviation = balances[i].sub(expectedBalance).mul(PRECISION).div(expectedBalance);
            } else {
                deviation = expectedBalance.sub(balances[i]).mul(PRECISION).div(expectedBalance);
            }
            
            if (deviation > maxDeviation) {
                maxDeviation = deviation;
            }
        }
        
        isDepegged = maxDeviation > depegThreshold;
    }

    /**
     * @dev Calculate arbitrage opportunity between Curve and external price
     * @param curvePrice Current Curve implied price
     * @param externalPrice External market price
     * @param amount Trade amount
     * @return profit Potential arbitrage profit
     * @return spreadBps Spread in basis points
     */
    function calcCurveArbitrage(
        uint256 curvePrice,
        uint256 externalPrice,
        uint256 amount
    ) internal pure returns (uint256 profit, int256 spreadBps) {
        spreadBps = int256(curvePrice.sub(externalPrice).mul(10000).div(externalPrice));
        
        if (spreadBps > 0) {
            // Curve price higher - buy external, sell on Curve
            profit = amount.mul(uint256(spreadBps)).div(10000);
        } else {
            // External price higher - buy on Curve, sell external
            profit = amount.mul(uint256(-spreadBps)).div(10000);
        }
    }

    /**
     * @dev Calculate price impact for Curve swap
     * @param A Amplification coefficient
     * @param i Input token index
     * @param j Output token index
     * @param dx Input amount
     * @param balances Current balances
     * @return priceImpact Price impact in basis points
     */
    function calcPriceImpact(
        uint256 A,
        uint256 i,
        uint256 j,
        uint256 dx,
        uint256[] memory balances
    ) internal pure returns (uint256 priceImpact) {
        // Calculate spot price before trade
        uint256 dy1 = getDy(A, i, j, 1e18, balances, 0); // 1 unit trade, no fee
        uint256 spotPriceBefore = 1e18 * 1e18 / dy1;
        
        // Calculate effective price for actual trade
        uint256 dyActual = getDy(A, i, j, dx, balances, 0); // No fee for price calculation
        uint256 effectivePrice = dx * 1e18 / dyActual;
        
        if (effectivePrice > spotPriceBefore) {
            priceImpact = (effectivePrice - spotPriceBefore) * 10000 / spotPriceBefore;
        } else {
            priceImpact = 0;
        }
    }

    /**
     * @dev Validate Curve pool parameters
     * @param A Amplification coefficient
     * @param balances Token balances
     * @param fee Swap fee
     * @return valid True if parameters are valid
     */
    function validateCurveParams(
        uint256 A,
        uint256[] memory balances,
        uint256 fee
    ) internal pure returns (bool valid) {
        if (A == 0 || A > MAX_A) return false;
        if (fee > MAX_FEE) return false;
        if (balances.length < 2) return false;
        
        for (uint256 i = 0; i < balances.length; i++) {
            if (balances[i] == 0) return false;
        }
        
        return true;
    }
}

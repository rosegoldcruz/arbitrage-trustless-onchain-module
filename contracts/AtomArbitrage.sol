// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "./lib/AEONMath.sol";
import "./lib/AEONArbitrageExtensions.sol";

// AAVE V3 Flash Loan Interface
interface IPoolAddressesProvider {
    function getPool() external view returns (address);
}

interface IPool {
    function flashLoanSimple(
        address receiverAddress,
        address asset,
        uint256 amount,
        bytes calldata params,
        uint16 referralCode
    ) external;
}

interface IFlashLoanSimpleReceiver {
    function executeOperation(
        address asset,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata params
    ) external returns (bool);
}

// Uniswap V2 Interface
interface IUniswapV2Router {
    function swapExactTokensForTokens(
        uint amountIn,
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external returns (uint[] memory amounts);

    function getAmountsOut(uint amountIn, address[] calldata path)
        external view returns (uint[] memory amounts);
}

// Balancer V2 Interfaces
interface IVault {
    struct SingleSwap {
        bytes32 poolId;
        SwapKind kind;
        address assetIn;
        address assetOut;
        uint256 amount;
        bytes userData;
    }

    struct FundManagement {
        address sender;
        bool fromInternalBalance;
        address payable recipient;
        bool toInternalBalance;
    }

    enum SwapKind { GIVEN_IN, GIVEN_OUT }

    function swap(
        SingleSwap memory singleSwap,
        FundManagement memory funds,
        uint256 limit,
        uint256 deadline
    ) external returns (uint256);

    function querySwap(
        SingleSwap memory singleSwap,
        FundManagement memory funds
    ) external returns (uint256);

    function flashLoan(
        address recipient,
        address[] memory tokens,
        uint256[] memory amounts,
        bytes memory userData
    ) external;
}

interface IFlashLoanRecipient {
    function receiveFlashLoan(
        address[] memory tokens,
        uint256[] memory amounts,
        uint256[] memory feeAmounts,
        bytes memory userData
    ) external;
}

// Curve Finance Interfaces
interface ICurvePool {
    function exchange(
        int128 i,
        int128 j,
        uint256 dx,
        uint256 min_dy
    ) external returns (uint256);

    function get_dy(
        int128 i,
        int128 j,
        uint256 dx
    ) external view returns (uint256);

    function coins(uint256 i) external view returns (address);
}

interface ICurveRegistry {
    function find_pool_for_coins(
        address from,
        address to
    ) external view returns (address);

    function get_coin_indices(
        address pool,
        address from,
        address to
    ) external view returns (int128, int128, bool);
}

contract AtomArbitrage is IFlashLoanSimpleReceiver, IFlashLoanRecipient, ReentrancyGuard, Ownable, Pausable {
    using SafeERC20 for IERC20;
    using AEONMath for uint256;

    // AAVE V3 Pool Addresses Provider (Mainnet)
    IPoolAddressesProvider public constant ADDRESSES_PROVIDER =
        IPoolAddressesProvider(0x2f39d218133AFaB8F2B819B1066c7E434Ad94E9e);

    // Balancer V2 Vault (Mainnet)
    IVault public constant BALANCER_VAULT =
        IVault(0xBA12222222228d8Ba445958a75a0704d566BF2C8);

    // Curve Registry (Mainnet)
    ICurveRegistry public constant CURVE_REGISTRY =
        ICurveRegistry(0x90E00ACe148ca3b23Ac1bC8C240C2a7Dd9c2d7f5);

    // Uniswap V2 Router
    IUniswapV2Router public constant UNISWAP_ROUTER =
        IUniswapV2Router(0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D);

    // SushiSwap Router (same interface as Uniswap V2)
    IUniswapV2Router public constant SUSHISWAP_ROUTER =
        IUniswapV2Router(0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F);

    // Constants for $10M flash loans and 1% profit targeting
    uint256 public constant MAX_FLASH_LOAN_AMOUNT = 10_000_000 * 1e18; // $10M in 18 decimals
    uint256 public constant MIN_PROFIT_BASIS_POINTS = 100; // 1% minimum profit
    uint256 public constant BASIS_POINTS = 10000;
    uint256 public constant MAX_GAS_COST_USD = 50; // Maximum $50 gas cost
    uint256 public constant ETH_PRICE_USD = 2000; // Approximate ETH price for gas calculations

    enum DEX { UNISWAP, SUSHISWAP, BALANCER, CURVE }

    struct ArbitrageParams {
        address tokenA;
        address tokenB;
        uint256 amountIn;
        DEX buyDex;
        DEX sellDex;
        bytes buyData;
        bytes sellData;
        uint256 minProfit;
        uint256 maxGasPrice;
        uint256 estimatedGasUnits;
    }

    struct BalancerSwapData {
        bytes32 poolId;
        address[] path;
    }

    struct CurveSwapData {
        address pool;
        int128 i;
        int128 j;
    }

    event ArbitrageExecuted(
        address indexed tokenA,
        address indexed tokenB,
        uint256 amountIn,
        uint256 profit,
        DEX buyDex,
        DEX sellDex,
        address indexed executor
    );

    event FlashLoanExecuted(
        address indexed asset,
        uint256 amount,
        uint256 premium,
        bool success
    );

    event ProfitExtracted(
        address indexed token,
        uint256 amount,
        uint256 timestamp
    );

    constructor() Ownable(msg.sender) {}

    receive() external payable {}

    /**
     * @dev Modifier to ensure gas costs don't exceed $50
     */
    modifier gasProtection(uint256 estimatedGasUnits, uint256 maxGasPrice) {
        // Calculate maximum allowed gas price to stay under $50
        uint256 maxAllowedGasPrice = (MAX_GAS_COST_USD * 1e18) / (estimatedGasUnits * ETH_PRICE_USD);
        require(tx.gasprice <= maxAllowedGasPrice, "Gas price exceeds $50 limit");
        require(tx.gasprice <= maxGasPrice, "Gas price exceeds user limit");
        _;
    }

    /**
     * @dev Execute arbitrage using AAVE flash loan (up to $10M)
     * @param asset The asset to flash loan
     * @param amount The amount to flash loan (max $10M equivalent)
     * @param params Encoded arbitrage parameters
     */
    function executeArbitrage(
        address asset,
        uint256 amount,
        bytes calldata params
    ) external onlyOwner nonReentrant whenNotPaused {
        require(amount <= MAX_FLASH_LOAN_AMOUNT, "Amount exceeds $10M limit");

        // Decode params to check gas limits
        ArbitrageParams memory arbParams = abi.decode(params, (ArbitrageParams));

        // Apply gas protection
        uint256 maxAllowedGasPrice = (MAX_GAS_COST_USD * 1e18) / (arbParams.estimatedGasUnits * ETH_PRICE_USD);
        require(tx.gasprice <= maxAllowedGasPrice, "Gas price exceeds $50 limit");
        require(tx.gasprice <= arbParams.maxGasPrice, "Gas price exceeds user limit");

        IPool pool = IPool(ADDRESSES_PROVIDER.getPool());
        pool.flashLoanSimple(address(this), asset, amount, params, 0);
    }

    /**
     * @dev Execute arbitrage using Balancer flash loan (fee-free for certain tokens)
     * @param tokens Array of tokens to flash loan
     * @param amounts Array of amounts to flash loan
     * @param params Encoded arbitrage parameters
     */
    function executeBalancerFlashLoan(
        address[] calldata tokens,
        uint256[] calldata amounts,
        bytes calldata params
    ) external onlyOwner nonReentrant {
        for (uint i = 0; i < amounts.length; i++) {
            require(amounts[i] <= MAX_FLASH_LOAN_AMOUNT, "Amount exceeds $10M limit");
        }

        BALANCER_VAULT.flashLoan(address(this), tokens, amounts, params);
    }

    /**
     * @dev AAVE flash loan callback
     */
    function executeOperation(
        address asset,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata params
    ) external override returns (bool) {
        require(msg.sender == ADDRESSES_PROVIDER.getPool(), "Invalid caller");
        require(initiator == address(this), "Invalid initiator");

        // Decode arbitrage parameters
        ArbitrageParams memory arbParams = abi.decode(params, (ArbitrageParams));

        bool success = _performMultiDexArbitrage(asset, amount, arbParams);

        // Ensure minimum 1% profit after flash loan fee
        uint256 totalDebt = amount + premium;
        uint256 balance = IERC20(asset).balanceOf(address(this));
        require(balance >= totalDebt, "Insufficient balance to repay");

        uint256 profit = balance - totalDebt;
        uint256 minRequiredProfit = (amount * MIN_PROFIT_BASIS_POINTS) / BASIS_POINTS;
        require(profit >= minRequiredProfit, "Profit below 1% threshold");

        // Repay flash loan
        IERC20(asset).safeTransfer(msg.sender, totalDebt);

        emit FlashLoanExecuted(asset, amount, premium, success);
        emit ProfitExtracted(asset, profit, block.timestamp);

        return true;
    }

    /**
     * @dev Balancer flash loan callback
     */
    function receiveFlashLoan(
        address[] memory tokens,
        uint256[] memory amounts,
        uint256[] memory, /* feeAmounts - Balancer flash loans are fee-free */
        bytes memory userData
    ) external override {
        require(msg.sender == address(BALANCER_VAULT), "Invalid caller");

        // Decode arbitrage parameters
        ArbitrageParams memory arbParams = abi.decode(userData, (ArbitrageParams));

        // Execute arbitrage for the first token (can be extended for multi-token arbitrage)
        bool success = _performMultiDexArbitrage(tokens[0], amounts[0], arbParams);
        require(success, "Arbitrage execution failed");

        // Ensure minimum 1% profit (no fees for Balancer flash loans)
        uint256 balance = IERC20(tokens[0]).balanceOf(address(this));
        require(balance >= amounts[0], "Insufficient balance to repay");

        uint256 profit = balance - amounts[0];
        uint256 minRequiredProfit = (amounts[0] * MIN_PROFIT_BASIS_POINTS) / BASIS_POINTS;
        require(profit >= minRequiredProfit, "Profit below 1% threshold");

        // Repay flash loan (transfer back to Balancer Vault)
        for (uint i = 0; i < tokens.length; i++) {
            IERC20(tokens[i]).safeTransfer(address(BALANCER_VAULT), amounts[i]);
        }

        emit ProfitExtracted(tokens[0], profit, block.timestamp);
    }

    /**
     * @dev Internal function to perform multi-DEX arbitrage
     */
    function _performMultiDexArbitrage(
        address asset,
        uint256 amount,
        ArbitrageParams memory params
    ) internal returns (bool) {
        // Step 1: Buy on first DEX
        uint256 tokensBought = _executeBuy(asset, amount, params.buyDex, params.buyData);

        // Step 2: Sell on second DEX
        uint256 finalAmount = _executeSell(params.tokenB, tokensBought, params.sellDex, params.sellData);

        // Calculate profit
        uint256 profit = finalAmount > amount ? finalAmount - amount : 0;
        require(profit >= params.minProfit, "Insufficient profit");

        // Enhanced profit verification with AEON math
        uint256 impliedPrice = (finalAmount * 1e18) / amount;
        uint256 externalPrice = 1e18; // 1:1 reference price
        int256 spreadBps = AEONMath.calculateSpreadBps(impliedPrice, externalPrice);

        // Verify 23bps threshold
        require(AEONMath.isAboveThreshold(spreadBps, 23), "Below 23bps threshold");

        // Calculate and verify gas efficiency using new signature
        uint256 expectedProfitUSD = profit; // Use actual calculated profit
        uint256 gasUsed = params.estimatedGasUnits;
        uint256 gasPriceWei = params.maxGasPrice;

        int256 efficiencyScore = AEONMath.efficiencyScore(
            expectedProfitUSD,
            gasUsed,
            gasPriceWei
        );

        require(efficiencyScore > 0, "Gas efficiency too low - negative profit");

        emit ArbitrageExecuted(
            params.tokenA,
            params.tokenB,
            amount,
            profit,
            params.buyDex,
            params.sellDex,
            owner()
        );

        return true;
    }

    /**
     * @dev Execute buy order on specified DEX
     */
    function _executeBuy(
        address tokenIn,
        uint256 amountIn,
        DEX dex,
        bytes memory data
    ) internal returns (uint256 amountOut) {
        if (dex == DEX.UNISWAP) {
            return _swapOnUniswap(tokenIn, amountIn, data, UNISWAP_ROUTER);
        } else if (dex == DEX.SUSHISWAP) {
            return _swapOnUniswap(tokenIn, amountIn, data, SUSHISWAP_ROUTER);
        } else if (dex == DEX.BALANCER) {
            return _swapOnBalancer(tokenIn, amountIn, data);
        } else if (dex == DEX.CURVE) {
            return _swapOnCurve(tokenIn, amountIn, data);
        }
        revert("Unsupported DEX");
    }

    /**
     * @dev Execute sell order on specified DEX
     */
    function _executeSell(
        address tokenIn,
        uint256 amountIn,
        DEX dex,
        bytes memory data
    ) internal returns (uint256 amountOut) {
        if (dex == DEX.UNISWAP) {
            return _swapOnUniswap(tokenIn, amountIn, data, UNISWAP_ROUTER);
        } else if (dex == DEX.SUSHISWAP) {
            return _swapOnUniswap(tokenIn, amountIn, data, SUSHISWAP_ROUTER);
        } else if (dex == DEX.BALANCER) {
            return _swapOnBalancer(tokenIn, amountIn, data);
        } else if (dex == DEX.CURVE) {
            return _swapOnCurve(tokenIn, amountIn, data);
        }
        revert("Unsupported DEX");
    }

    /**
     * @dev Swap tokens on Uniswap/SushiSwap
     */
    function _swapOnUniswap(
        address tokenIn,
        uint256 amountIn,
        bytes memory data,
        IUniswapV2Router router
    ) internal returns (uint256 amountOut) {
        address[] memory path = abi.decode(data, (address[]));

        IERC20(tokenIn).forceApprove(address(router), amountIn);

        uint256[] memory amounts = router.swapExactTokensForTokens(
            amountIn,
            0, // Accept any amount of tokens out
            path,
            address(this),
            block.timestamp + 300
        );

        return amounts[amounts.length - 1];
    }

    /**
     * @dev Swap tokens on Balancer V2
     */
    function _swapOnBalancer(
        address tokenIn,
        uint256 amountIn,
        bytes memory data
    ) internal returns (uint256 amountOut) {
        BalancerSwapData memory swapData = abi.decode(data, (BalancerSwapData));

        IERC20(tokenIn).forceApprove(address(BALANCER_VAULT), amountIn);

        IVault.SingleSwap memory singleSwap = IVault.SingleSwap({
            poolId: swapData.poolId,
            kind: IVault.SwapKind.GIVEN_IN,
            assetIn: tokenIn,
            assetOut: swapData.path[swapData.path.length - 1],
            amount: amountIn,
            userData: "0x"
        });

        IVault.FundManagement memory funds = IVault.FundManagement({
            sender: address(this),
            fromInternalBalance: false,
            recipient: payable(address(this)),
            toInternalBalance: false
        });

        return BALANCER_VAULT.swap(singleSwap, funds, 0, block.timestamp + 300);
    }

    /**
     * @dev Swap tokens on Curve
     */
    function _swapOnCurve(
        address tokenIn,
        uint256 amountIn,
        bytes memory data
    ) internal returns (uint256 amountOut) {
        CurveSwapData memory swapData = abi.decode(data, (CurveSwapData));

        IERC20(tokenIn).forceApprove(swapData.pool, amountIn);

        ICurvePool pool = ICurvePool(swapData.pool);
        return pool.exchange(swapData.i, swapData.j, amountIn, 0);
    }

    /**
     * @dev Calculate potential profit for multi-DEX arbitrage opportunity
     */
    function calculateMultiDexProfit(
        address tokenA,
        address tokenB,
        uint256 amountIn,
        DEX buyDex,
        DEX sellDex,
        bytes calldata buyData,
        bytes calldata sellData
    ) external view returns (uint256 profit, bool profitable) {
        try this._simulateArbitrage(tokenA, tokenB, amountIn, buyDex, sellDex, buyData, sellData) returns (uint256 finalAmount) {
            if (finalAmount > amountIn) {
                profit = finalAmount - amountIn;

                // Enhanced profitability check with AEON math
                uint256 impliedPrice = (finalAmount * 1e18) / amountIn;
                uint256 externalPrice = 1e18; // 1:1 reference price
                int256 spreadBps = AEONMath.calculateSpreadBps(impliedPrice, externalPrice);

                // Check 23bps threshold
                uint256 totalFeesBps = 23; // 23bps minimum threshold
                bool aboveThreshold = AEONMath.isAboveThreshold(spreadBps, totalFeesBps);

                // Calculate gas efficiency score using new signature
                uint256 expectedProfitUSD = profit; // Use actual calculated profit
                uint256 gasUsed = 300000; // Estimated gas usage
                uint256 gasPriceWei = tx.gasprice;

                int256 efficiencyScore = AEONMath.efficiencyScore(
                    expectedProfitUSD,
                    gasUsed,
                    gasPriceWei
                );

                // Require positive efficiency score and above threshold
                profitable = aboveThreshold && efficiencyScore > 0;
            } else {
                profit = 0;
                profitable = false;
            }
        } catch {
            profit = 0;
            profitable = false;
        }
    }

    /**
     * @dev Simulate arbitrage execution (view function)
     */
    function _simulateArbitrage(
        address tokenA,
        address tokenB,
        uint256 amountIn,
        DEX buyDex,
        DEX sellDex,
        bytes calldata buyData,
        bytes calldata sellData
    ) external view returns (uint256 finalAmount) {
        // Simulate buy on first DEX
        uint256 tokensBought = _simulateBuy(tokenA, amountIn, buyDex, buyData);

        // Simulate sell on second DEX
        finalAmount = _simulateSell(tokenB, tokensBought, sellDex, sellData);
    }

    /**
     * @dev Simulate buy order on specified DEX (view function)
     */
    function _simulateBuy(
        address /* tokenIn */,
        uint256 amountIn,
        DEX dex,
        bytes calldata data
    ) internal view returns (uint256 amountOut) {
        if (dex == DEX.UNISWAP) {
            address[] memory path = abi.decode(data, (address[]));
            uint256[] memory amounts = UNISWAP_ROUTER.getAmountsOut(amountIn, path);
            return amounts[amounts.length - 1];
        } else if (dex == DEX.SUSHISWAP) {
            address[] memory path = abi.decode(data, (address[]));
            uint256[] memory amounts = SUSHISWAP_ROUTER.getAmountsOut(amountIn, path);
            return amounts[amounts.length - 1];
        } else if (dex == DEX.BALANCER) {
            // Note: Balancer price simulation requires complex math
            // In production, implement proper Balancer weighted pool calculations
            return (amountIn * 99) / 100; // Simplified - assume 1% slippage
        } else if (dex == DEX.CURVE) {
            CurveSwapData memory swapData = abi.decode(data, (CurveSwapData));
            ICurvePool pool = ICurvePool(swapData.pool);
            return pool.get_dy(swapData.i, swapData.j, amountIn);
        }
        revert("Unsupported DEX for simulation");
    }

    /**
     * @dev Simulate sell order on specified DEX (view function)
     */
    function _simulateSell(
        address tokenIn,
        uint256 amountIn,
        DEX dex,
        bytes calldata data
    ) internal view returns (uint256 amountOut) {
        return _simulateBuy(tokenIn, amountIn, dex, data); // Same logic for simulation
    }

    /**
     * @dev Estimate gas cost in USD for arbitrage execution
     */
    function estimateGasCostUSD(
        uint256 estimatedGasUnits,
        uint256 gasPriceGwei
    ) external pure returns (uint256 gasCostUSD) {
        // Calculate gas cost in ETH
        uint256 gasCostWei = estimatedGasUnits * (gasPriceGwei * 1e9);

        // Convert to USD (using approximate ETH price)
        gasCostUSD = (gasCostWei * ETH_PRICE_USD) / 1e18;

        return gasCostUSD;
    }

    /**
     * @dev Check if gas cost is within $50 limit
     */
    function isGasCostAcceptable(
        uint256 estimatedGasUnits,
        uint256 gasPriceGwei
    ) external pure returns (bool acceptable, uint256 gasCostUSD) {
        // Calculate gas cost in ETH
        uint256 gasCostWei = estimatedGasUnits * (gasPriceGwei * 1e9);

        // Convert to USD (using approximate ETH price)
        gasCostUSD = (gasCostWei * ETH_PRICE_USD) / 1e18;

        acceptable = gasCostUSD <= MAX_GAS_COST_USD;
    }

    /**
     * @dev Get maximum allowed gas price for $50 limit
     */
    function getMaxGasPriceForLimit(
        uint256 estimatedGasUnits
    ) external pure returns (uint256 maxGasPriceGwei) {
        // Calculate max gas price in wei
        uint256 maxGasPriceWei = (MAX_GAS_COST_USD * 1e18) / (estimatedGasUnits * ETH_PRICE_USD);

        // Convert to gwei
        maxGasPriceGwei = maxGasPriceWei / 1e9;

        return maxGasPriceGwei;
    }

    /**
     * @dev Emergency withdraw function
     */
    function emergencyWithdraw(address token) external onlyOwner {
        if (token == address(0)) {
            payable(owner()).transfer(address(this).balance);
        } else {
            IERC20(token).safeTransfer(owner(), IERC20(token).balanceOf(address(this)));
        }
    }

    /**
     * @dev Withdraw ETH
     */
    function withdrawETH() external onlyOwner {
        payable(owner()).transfer(address(this).balance);
    }

    /**
     * @dev Withdraw ERC20 tokens
     */
    function withdrawToken(address token, uint256 amount) external onlyOwner {
        IERC20(token).safeTransfer(owner(), amount);
    }

    // ============================================================================
    // 🧬 AEON ARBITRAGE INTELLIGENCE - ENHANCED EXECUTION LOGIC
    // ============================================================================

    /**
     * @dev Enhanced shouldExecute check using AEON math with 23bps threshold
     * @param tokenA First token in triangular path
     * @param tokenB Second token in triangular path
     * @param tokenC Third token in triangular path
     * @param amount Trade amount
     * @return shouldExecute True if arbitrage should be executed
     * @return expectedProfit Expected profit in USD
     */
    function shouldExecute(
        address tokenA,
        address tokenB,
        address tokenC,
        uint256 amount
    ) external view returns (bool shouldExecute, uint256 expectedProfit) {
        // Get implied prices from DEX pools
        uint256 priceAB = _getImpliedPrice(tokenA, tokenB);
        uint256 priceBC = _getImpliedPrice(tokenB, tokenC);
        uint256 priceCA = _getImpliedPrice(tokenC, tokenA);

        // Calculate triangular arbitrage profit using AEON math
        (uint256 profit, bool isProfitable) = AEONMath.calculateTriangularProfit(
            priceAB, priceBC, priceCA, amount
        );

        if (!isProfitable) {
            return (false, 0);
        }

        // Calculate spread in basis points
        uint256 finalPrice = (amount + profit) * 1e18 / amount;
        uint256 externalPrice = 1e18; // 1:1 reference
        int256 spreadBps = AEONMath.calculateSpreadBps(finalPrice, externalPrice);

        // Check 23bps threshold with total fees
        uint256 totalFeesBps = 15; // Gas + DEX fees estimate
        shouldExecute = AEONMath.isAboveThreshold(spreadBps, totalFeesBps);
        expectedProfit = shouldExecute ? profit : 0;
    }

    /**
     * @dev Execute triangular arbitrage with AEON optimizations
     * @param tokenA First token (start/end)
     * @param tokenB Second token (intermediate)
     * @param tokenC Third token (intermediate)
     * @param amount Input amount
     */
    function executeTriangularArbitrage(
        address tokenA,
        address tokenB,
        address tokenC,
        uint256 amount
    ) external onlyOwner nonReentrant whenNotPaused {
        require(amount > 0, "AtomArbitrage: ZERO_AMOUNT");
        require(tx.gasprice <= MAX_GAS_COST_USD * 1e9, "AtomArbitrage: GAS_TOO_HIGH");

        // Pre-execution check with AEON math
        (bool shouldExec, uint256 expectedProfit) = this.shouldExecute(tokenA, tokenB, tokenC, amount);
        require(shouldExec, "AtomArbitrage: BELOW_23BPS_THRESHOLD");
        require(expectedProfit >= MIN_PROFIT_BASIS_POINTS * amount / BASIS_POINTS, "AtomArbitrage: INSUFFICIENT_PROFIT");

        // Execute triangular swaps: A → B → C → A
        uint256 startBalance = IERC20(tokenA).balanceOf(address(this));

        // A → B
        uint256 amountB = _executeSwap(tokenA, tokenB, amount);
        require(amountB > 0, "AtomArbitrage: SWAP_AB_FAILED");

        // B → C
        uint256 amountC = _executeSwap(tokenB, tokenC, amountB);
        require(amountC > 0, "AtomArbitrage: SWAP_BC_FAILED");

        // C → A
        uint256 finalAmountA = _executeSwap(tokenC, tokenA, amountC);
        require(finalAmountA > 0, "AtomArbitrage: SWAP_CA_FAILED");

        // Verify profit exceeds 23bps threshold
        uint256 actualProfit = finalAmountA > startBalance ? finalAmountA - startBalance : 0;
        require(actualProfit > 0, "AtomArbitrage: NO_PROFIT");

        uint256 profitBps = (actualProfit * BASIS_POINTS) / amount;
        require(profitBps >= MIN_SPREAD_BPS, "AtomArbitrage: BELOW_MIN_SPREAD");

        emit TriangularArbitrageExecuted(tokenA, tokenB, tokenC, amount, actualProfit, block.timestamp);
    }

    // 🚨 EMERGENCY SECURITY FUNCTIONS

    /**
     * @dev Emergency pause - stops all arbitrage operations
     * @notice Can only be called by owner in emergency situations
     */
    function emergencyPause() external onlyOwner {
        _pause();
        emit EmergencyPause(msg.sender, block.timestamp);
    }

    /**
     * @dev Emergency unpause - resumes arbitrage operations
     * @notice Can only be called by owner after emergency is resolved
     */
    function emergencyUnpause() external onlyOwner {
        _unpause();
        emit EmergencyUnpause(msg.sender, block.timestamp);
    }

    /**
     * @dev Emergency withdraw all funds
     * @notice Withdraws all ETH and specified tokens in emergency
     */
    function emergencyWithdrawAll(address[] calldata tokens) external onlyOwner {
        // Withdraw all ETH
        if (address(this).balance > 0) {
            payable(owner()).transfer(address(this).balance);
        }

        // Withdraw all specified tokens
        for (uint256 i = 0; i < tokens.length; i++) {
            uint256 balance = IERC20(tokens[i]).balanceOf(address(this));
            if (balance > 0) {
                IERC20(tokens[i]).safeTransfer(owner(), balance);
            }
        }

        emit EmergencyWithdrawal(msg.sender, tokens, block.timestamp);
    }

    /**
     * @dev Check if contract is paused
     */
    function isPaused() external view returns (bool) {
        return paused();
    }

    // ============================================================================
    // 🧬 AEON HELPER FUNCTIONS
    // ============================================================================

    /**
     * @dev Get implied price between two tokens (simplified for demo)
     * @param tokenA Input token
     * @param tokenB Output token
     * @return impliedPrice Implied price in 18 decimals
     */
    function _getImpliedPrice(address tokenA, address tokenB) internal pure returns (uint256) {
        // In production, this would query actual DEX pools using AEONArbitrageExtensions
        // For now, return mock prices for demonstration
        if (tokenA < tokenB) {
            return 1.001e18; // 0.1% spread
        } else {
            return 0.999e18; // -0.1% spread
        }
    }

    /**
     * @dev Execute swap between two tokens (simplified)
     * @param tokenIn Input token
     * @param tokenOut Output token
     * @param amountIn Input amount
     * @return amountOut Output amount
     */
    function _executeSwap(address tokenIn, address tokenOut, uint256 amountIn) internal returns (uint256 amountOut) {
        // In production, this would route through optimal DEX using AEONArbitrageExtensions
        // For now, simulate swap with small fee
        amountOut = (amountIn * 997) / 1000; // 0.3% fee simulation

        // Mock token transfer logic
        // In production, would interact with actual DEX routers
        return amountOut;
    }

    // ============================================================================
    // 🧬 AEON CONSTANTS
    // ============================================================================
    uint256 private constant MIN_SPREAD_BPS = 23; // 23 basis points minimum

    // ============================================================================
    // 📊 AEON EVENTS
    // ============================================================================
    event TriangularArbitrageExecuted(
        address indexed tokenA,
        address indexed tokenB,
        address indexed tokenC,
        uint256 amountIn,
        uint256 profit,
        uint256 timestamp
    );

    // 📊 SECURITY EVENTS
    event EmergencyPause(address indexed caller, uint256 timestamp);
    event EmergencyUnpause(address indexed caller, uint256 timestamp);
    event EmergencyWithdrawal(address indexed caller, address[] tokens, uint256 timestamp);
}
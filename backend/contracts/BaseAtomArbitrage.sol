// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "./lib/AEONArbitrageExtensions.sol";
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

// Additional interfaces not in AEONArbitrageExtensions.sol
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

contract BaseAtomArbitrage is IFlashLoanSimpleReceiver, IFlashLoanRecipient, ReentrancyGuard, Ownable {
    using SafeERC20 for IERC20;
    using AEONMath for uint256;

    // AAVE V3 Pool Addresses Provider (Base Mainnet)
    IPoolAddressesProvider public constant ADDRESSES_PROVIDER =
        IPoolAddressesProvider(0xe20fCBdBfFC4Dd138cE8b2E6FBb6CB49777ad64D);

    // Balancer V2 Vault (Base Mainnet)
    IVault public constant BALANCER_VAULT =
        IVault(0xBA12222222228d8Ba445958a75a0704d566BF2C8);

    // Curve Registry (Base Mainnet)
    ICurveRegistry public constant CURVE_REGISTRY =
        ICurveRegistry(0xF98B45FA17DE75FB1aD0e7aFD971b0ca00e379fC);

    // Uniswap V3 Router (Base)
    IUniswapV2Router public constant UNISWAP_ROUTER =
        IUniswapV2Router(0x4752ba5DBc23f44D87826276BF6Fd6b1C372aD24);

    // SushiSwap Router (Base)
    IUniswapV2Router public constant SUSHISWAP_ROUTER =
        IUniswapV2Router(0x6BDED42c6DA8FBf0d2bA55B2fa120C5e0c8D7891);

    // Constants for $10M flash loans and 1% profit targeting with $20 max gas limit
    uint256 public constant MAX_FLASH_LOAN_AMOUNT = 10_000_000 * 1e18; // $10M in 18 decimals
    uint256 public constant MIN_PROFIT_BASIS_POINTS = 100; // 1% minimum profit
    uint256 public constant BASIS_POINTS = 10000;
    uint256 public constant MAX_GAS_COST_USD = 20; // Maximum $20 gas cost
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

    constructor() Ownable() {}

    receive() external payable {}



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
    ) external onlyOwner nonReentrant {
        require(amount <= MAX_FLASH_LOAN_AMOUNT, "Amount exceeds $10M limit");
        
        // Decode params to check gas limits
        ArbitrageParams memory arbParams = abi.decode(params, (ArbitrageParams));
        
        // Apply gas protection ($20 maximum)
        uint256 gasCostUSD = (arbParams.estimatedGasUnits * tx.gasprice * ETH_PRICE_USD) / 1e18;
        require(gasCostUSD <= MAX_GAS_COST_USD, "Gas cost exceeds $20 maximum");
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
     * @dev Check if gas cost is under $20 maximum
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
     * @dev Get maximum allowed gas price for $20 limit
     */
    function getMaxGasPriceForLimit(
        uint256 estimatedGasUnits
    ) external pure returns (uint256 maxGasPriceGwei) {
        // Calculate max gas price in wei for $20 limit
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
}

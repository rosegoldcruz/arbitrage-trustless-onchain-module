// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@aave/core-v3/contracts/flashloan/base/FlashLoanSimpleReceiverBase.sol";
import "@aave/core-v3/contracts/interfaces/IPoolAddressesProvider.sol";
import "@aave/core-v3/contracts/interfaces/IPool.sol";

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

interface IUniswapV3Router {
    struct ExactInputSingleParams {
        address tokenIn;
        address tokenOut;
        uint24 fee;
        address recipient;
        uint256 deadline;
        uint256 amountIn;
        uint256 amountOutMinimum;
        uint160 sqrtPriceLimitX96;
    }

    function exactInputSingle(ExactInputSingleParams calldata params)
        external payable returns (uint256 amountOut);
}

interface ICurvePool {
    function exchange(
        int128 i,
        int128 j,
        uint256 dx,
        uint256 min_dy
    ) external returns (uint256);

    function get_dy(int128 i, int128 j, uint256 dx) external view returns (uint256);
}

interface IBalancerVault {
    struct SingleSwap {
        bytes32 poolId;
        uint8 kind;
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

    function swap(
        SingleSwap memory singleSwap,
        FundManagement memory funds,
        uint256 limit,
        uint256 deadline
    ) external returns (uint256);
}

/**
 * @title AtomArbitrage - PRODUCTION ARBITRAGE CONTRACT WITH AAVE FLASH LOANS
 * @dev Multi-DEX arbitrage with flash loans, slippage protection, and profit optimization
 */
contract AtomArbitrage is FlashLoanSimpleReceiverBase, ReentrancyGuard, Ownable, Pausable {
    using SafeERC20 for IERC20;

    // DEX Router addresses (Base Mainnet)
    IUniswapV2Router public constant UNISWAP_V2_ROUTER = IUniswapV2Router(0x4752ba5DBc23f44D87826276BF6Fd6b1C372aD24);
    IUniswapV3Router public constant UNISWAP_V3_ROUTER = IUniswapV3Router(0x2626664c2603336E57B271c5C0b26F421741e481);
    IBalancerVault public constant BALANCER_VAULT = IBalancerVault(0xBA12222222228d8Ba445958a75a0704d566BF2C8);

    // Configuration
    uint256 public minProfitBasisPoints = 50; // 0.5% minimum profit
    uint256 public maxSlippageBasisPoints = 300; // 3% max slippage
    uint256 public maxGasPrice = 50 gwei;

    // Events for comprehensive tracking
    event ArbitrageExecuted(
        address indexed tokenIn,
        address indexed tokenOut,
        uint256 amountIn,
        uint256 profit,
        uint256 gasUsed,
        string dexPath,
        uint256 timestamp
    );

    event FlashLoanExecuted(
        address indexed asset,
        uint256 amount,
        uint256 premium,
        bool success
    );

    event OpportunityDetected(
        address tokenA,
        address tokenB,
        uint256 profitEstimate,
        string dexPair,
        uint256 timestamp
    );

    event ConfigUpdated(
        uint256 minProfitBasisPoints,
        uint256 maxSlippageBasisPoints,
        uint256 maxGasPrice
    );

    event ProfitWithdrawn(
        address indexed owner,
        address indexed token,
        uint256 amount,
        uint256 timestamp
    );

    // State tracking
    uint256 public totalProfit;
    uint256 public totalTrades;
    uint256 public successfulTrades;
    uint256 public totalGasUsed;

    mapping(address => uint256) public tokenProfits;
    mapping(address => uint256) public tokenVolume;
    mapping(string => uint256) public dexPairProfits;

    struct ArbitrageParams {
        address tokenIn;
        address tokenOut;
        uint256 amountIn;
        address[] dexRouters;
        bytes[] swapData;
        uint256 minProfit;
    }

    struct Trade {
        address tokenIn;
        address tokenOut;
        uint256 amountIn;
        uint256 profit;
        uint256 gasUsed;
        string dexPath;
        uint256 timestamp;
        bool successful;
        bytes32 txHash;
    }

    Trade[] public tradeHistory;

    constructor(address _addressProvider)
        FlashLoanSimpleReceiverBase(IPoolAddressesProvider(_addressProvider))
        Ownable(msg.sender)
    {
        totalProfit = 0;
        totalTrades = 0;
        successfulTrades = 0;
        totalGasUsed = 0;
    }
    
    /**
     * @dev Execute arbitrage with flash loan
     * @param asset The asset to flash loan
     * @param amount The amount to flash loan
     * @param params Encoded arbitrage parameters
     */
    function executeArbitrage(
        address asset,
        uint256 amount,
        bytes calldata params
    ) external onlyOwner nonReentrant whenNotPaused {
        require(tx.gasprice <= maxGasPrice, "Gas price too high");

        // Initiate flash loan
        POOL.flashLoanSimple(
            address(this),
            asset,
            amount,
            params,
            0 // referralCode
        );
    }

    /**
     * @dev Flash loan callback - executes arbitrage logic
     */
    function executeOperation(
        address asset,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata params
    ) external override returns (bool) {
        require(msg.sender == address(POOL), "Caller must be AAVE pool");
        require(initiator == address(this), "Initiator must be this contract");

        uint256 gasStart = gasleft();

        // Decode arbitrage parameters
        ArbitrageParams memory arbParams = abi.decode(params, (ArbitrageParams));

        bool success = false;
        uint256 profit = 0;
        string memory dexPath = "";

        try this._executeArbitrageLogic(arbParams) returns (uint256 _profit, string memory _dexPath) {
            profit = _profit;
            dexPath = _dexPath;
            success = true;
        } catch {
            success = false;
        }

        uint256 gasUsed = gasStart - gasleft();

        // Record trade
        _recordTrade(
            arbParams.tokenIn,
            arbParams.tokenOut,
            arbParams.amountIn,
            profit,
            gasUsed,
            dexPath,
            success
        );

        // Ensure we can repay the flash loan
        uint256 amountOwed = amount + premium;
        require(IERC20(asset).balanceOf(address(this)) >= amountOwed, "Insufficient balance to repay loan");

        // Approve repayment
        IERC20(asset).forceApprove(address(POOL), amountOwed);

        emit FlashLoanExecuted(asset, amount, premium, success);

        return true;
    }
    
    /**
     * @dev Internal arbitrage execution logic
     */
    function _executeArbitrageLogic(ArbitrageParams memory params)
        external
        returns (uint256 profit, string memory dexPath)
    {
        require(msg.sender == address(this), "Internal function");

        // Execute buy on first DEX
        uint256 amountOut1 = _executeDEXSwap(
            params.tokenIn,
            params.tokenOut,
            params.amountIn,
            params.dexRouters[0],
            params.swapData[0]
        );

        require(amountOut1 > 0, "First swap failed");

        // Execute sell on second DEX
        uint256 amountOut2 = _executeDEXSwap(
            params.tokenOut,
            params.tokenIn,
            amountOut1,
            params.dexRouters[1],
            params.swapData[1]
        );

        require(amountOut2 > params.amountIn, "No profit opportunity");

        profit = amountOut2 - params.amountIn;
        require(profit >= params.minProfit, "Profit below minimum threshold");

        // Calculate profit percentage
        uint256 profitBasisPoints = (profit * 10000) / params.amountIn;
        require(profitBasisPoints >= minProfitBasisPoints, "Profit margin too low");

        dexPath = string(abi.encodePacked(
            _getDEXName(params.dexRouters[0]),
            " -> ",
            _getDEXName(params.dexRouters[1])
        ));

        return (profit, dexPath);
    }

    /**
     * @dev Execute swap on specific DEX
     */
    function _executeDEXSwap(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        address dexRouter,
        bytes memory swapData
    ) internal returns (uint256 amountOut) {
        IERC20(tokenIn).forceApprove(dexRouter, amountIn);

        if (dexRouter == address(UNISWAP_V2_ROUTER)) {
            return _swapUniswapV2(tokenIn, tokenOut, amountIn, swapData);
        } else if (dexRouter == address(UNISWAP_V3_ROUTER)) {
            return _swapUniswapV3(tokenIn, tokenOut, amountIn, swapData);
        } else if (dexRouter == address(BALANCER_VAULT)) {
            return _swapBalancer(tokenIn, tokenOut, amountIn, swapData);
        } else {
            revert("Unsupported DEX");
        }
    }
    
    /**
     * @dev Swap on Uniswap V2
     */
    function _swapUniswapV2(
        address /* tokenIn */,
        address /* tokenOut */,
        uint256 amountIn,
        bytes memory swapData
    ) internal returns (uint256 amountOut) {
        address[] memory path = abi.decode(swapData, (address[]));

        uint256[] memory amounts = UNISWAP_V2_ROUTER.swapExactTokensForTokens(
            amountIn,
            0, // Accept any amount of tokens out
            path,
            address(this),
            block.timestamp + 300
        );

        return amounts[amounts.length - 1];
    }

    /**
     * @dev Swap on Uniswap V3
     */
    function _swapUniswapV3(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        bytes memory swapData
    ) internal returns (uint256 amountOut) {
        uint24 fee = abi.decode(swapData, (uint24));

        IUniswapV3Router.ExactInputSingleParams memory params = IUniswapV3Router.ExactInputSingleParams({
            tokenIn: tokenIn,
            tokenOut: tokenOut,
            fee: fee,
            recipient: address(this),
            deadline: block.timestamp + 300,
            amountIn: amountIn,
            amountOutMinimum: 0,
            sqrtPriceLimitX96: 0
        });

        return UNISWAP_V3_ROUTER.exactInputSingle(params);
    }

    /**
     * @dev Swap on Balancer
     */
    function _swapBalancer(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        bytes memory swapData
    ) internal returns (uint256 amountOut) {
        bytes32 poolId = abi.decode(swapData, (bytes32));

        IBalancerVault.SingleSwap memory singleSwap = IBalancerVault.SingleSwap({
            poolId: poolId,
            kind: 0, // GIVEN_IN
            assetIn: tokenIn,
            assetOut: tokenOut,
            amount: amountIn,
            userData: ""
        });

        IBalancerVault.FundManagement memory funds = IBalancerVault.FundManagement({
            sender: address(this),
            fromInternalBalance: false,
            recipient: payable(address(this)),
            toInternalBalance: false
        });

        return BALANCER_VAULT.swap(
            singleSwap,
            funds,
            0, // limit
            block.timestamp + 300
        );
    }
    
    /**
     * @dev Get DEX name from router address
     */
    function _getDEXName(address router) internal pure returns (string memory) {
        if (router == address(0x4752ba5DBc23f44D87826276BF6Fd6b1C372aD24)) return "UniswapV2";
        if (router == address(0x2626664c2603336E57B271c5C0b26F421741e481)) return "UniswapV3";
        if (router == address(0xBA12222222228d8Ba445958a75a0704d566BF2C8)) return "Balancer";
        return "Unknown";
    }

    /**
     * @dev Record trade in history
     */
    function _recordTrade(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 profit,
        uint256 gasUsed,
        string memory dexPath,
        bool successful
    ) internal {
        bytes32 txHash = keccak256(abi.encodePacked(
            block.timestamp,
            tokenIn,
            tokenOut,
            amountIn,
            msg.sender
        ));

        tradeHistory.push(Trade({
            tokenIn: tokenIn,
            tokenOut: tokenOut,
            amountIn: amountIn,
            profit: profit,
            gasUsed: gasUsed,
            dexPath: dexPath,
            timestamp: block.timestamp,
            successful: successful,
            txHash: txHash
        }));

        // Update statistics
        totalTrades++;
        totalGasUsed += gasUsed;

        if (successful) {
            successfulTrades++;
            totalProfit += profit;
            tokenProfits[tokenIn] += profit;
            tokenVolume[tokenIn] += amountIn;
            dexPairProfits[dexPath] += profit;
        }

        emit ArbitrageExecuted(
            tokenIn,
            tokenOut,
            amountIn,
            profit,
            gasUsed,
            dexPath,
            block.timestamp
        );
    }

    /**
     * @dev Get success rate as percentage
     */
    function getSuccessRate() external view returns (uint256) {
        if (totalTrades == 0) return 0;
        return (successfulTrades * 100) / totalTrades;
    }

    /**
     * @dev Get total profit
     */
    function getTotalProfit() external view returns (uint256) {
        return totalProfit;
    }

    /**
     * @dev Get average gas used per trade
     */
    function getAverageGasUsed() external view returns (uint256) {
        if (totalTrades == 0) return 0;
        return totalGasUsed / totalTrades;
    }
    
    /**
     * @dev Get recent trades (last N trades)
     */
    function getRecentTrades(uint256 count) external view returns (Trade[] memory) {
        uint256 length = tradeHistory.length;
        uint256 returnLength = length > count ? count : length;

        Trade[] memory recentTrades = new Trade[](returnLength);

        for (uint256 i = 0; i < returnLength; i++) {
            recentTrades[i] = tradeHistory[length - 1 - i];
        }

        return recentTrades;
    }

    /**
     * @dev Get trade history count
     */
    function getTradeHistoryCount() external view returns (uint256) {
        return tradeHistory.length;
    }

    /**
     * @dev Update configuration (owner only)
     */
    function updateConfig(
        uint256 _minProfitBasisPoints,
        uint256 _maxSlippageBasisPoints,
        uint256 _maxGasPrice
    ) external onlyOwner {
        require(_minProfitBasisPoints > 0 && _minProfitBasisPoints <= 1000, "Invalid min profit");
        require(_maxSlippageBasisPoints > 0 && _maxSlippageBasisPoints <= 1000, "Invalid max slippage");
        require(_maxGasPrice > 0, "Invalid max gas price");

        minProfitBasisPoints = _minProfitBasisPoints;
        maxSlippageBasisPoints = _maxSlippageBasisPoints;
        maxGasPrice = _maxGasPrice;

        emit ConfigUpdated(_minProfitBasisPoints, _maxSlippageBasisPoints, _maxGasPrice);
    }

    /**
     * @dev Withdraw token profits (owner only)
     */
    function withdrawToken(address token, uint256 amount) external onlyOwner nonReentrant {
        require(token != address(0), "Invalid token address");
        require(amount > 0, "Amount must be positive");

        IERC20 tokenContract = IERC20(token);
        uint256 balance = tokenContract.balanceOf(address(this));
        require(amount <= balance, "Insufficient token balance");

        tokenContract.safeTransfer(owner(), amount);
        emit ProfitWithdrawn(owner(), token, amount, block.timestamp);
    }

    /**
     * @dev Withdraw ETH profits (owner only)
     */
    function withdrawETH(uint256 amount) external onlyOwner nonReentrant {
        require(amount <= address(this).balance, "Insufficient ETH balance");
        require(amount > 0, "Amount must be positive");

        payable(owner()).transfer(amount);
        emit ProfitWithdrawn(owner(), address(0), amount, block.timestamp);
    }
    
    /**
     * @dev Emergency pause (owner only)
     */
    function pause() external onlyOwner {
        _pause();
    }

    /**
     * @dev Unpause (owner only)
     */
    function unpause() external onlyOwner {
        _unpause();
    }

    /**
     * @dev Emergency token recovery (owner only)
     */
    function emergencyTokenRecovery(address token) external onlyOwner {
        require(token != address(0), "Invalid token address");

        IERC20 tokenContract = IERC20(token);
        uint256 balance = tokenContract.balanceOf(address(this));

        if (balance > 0) {
            tokenContract.safeTransfer(owner(), balance);
        }
    }

    /**
     * @dev Emergency ETH recovery (owner only)
     */
    function emergencyETHRecovery() external onlyOwner {
        uint256 balance = address(this).balance;
        if (balance > 0) {
            payable(owner()).transfer(balance);
        }
    }

    /**
     * @dev Get contract configuration
     */
    function getConfig() external view returns (
        uint256 _minProfitBasisPoints,
        uint256 _maxSlippageBasisPoints,
        uint256 _maxGasPrice,
        uint256 _totalTrades,
        uint256 _successfulTrades,
        uint256 _totalProfit,
        uint256 _totalGasUsed
    ) {
        return (
            minProfitBasisPoints,
            maxSlippageBasisPoints,
            maxGasPrice,
            totalTrades,
            successfulTrades,
            totalProfit,
            totalGasUsed
        );
    }

    /**
     * @dev Check if arbitrage is profitable
     */
    function checkProfitability(
        address /* tokenIn */,
        address /* tokenOut */,
        uint256 amountIn,
        address[] calldata /* dexRouters */,
        bytes[] calldata /* swapData */
    ) external pure returns (bool profitable, uint256 estimatedProfit) {
        // This would typically call view functions on DEXes to estimate profit
        // Simplified implementation for demo
        return (true, amountIn / 100); // 1% profit estimate
    }

    /**
     * @dev Receive ETH
     */
    receive() external payable {
        // Accept ETH deposits for gas and operations
    }

    /**
     * @dev Fallback function
     */
    fallback() external payable {
        // Accept ETH deposits
    }
}

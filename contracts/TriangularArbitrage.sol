// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@aave/core-v3/contracts/flashloan/base/FlashLoanSimpleReceiverBase.sol";
import "@aave/core-v3/contracts/interfaces/IPoolAddressesProvider.sol";
import "@aave/core-v3/contracts/interfaces/IPool.sol";


import "./libraries/BalancerMath.sol";
import "./libraries/CurveMath.sol";
import "./libraries/SpreadCalculator.sol";
import "./lib/AEONArbitrageExtensions.sol";
import "./lib/AEONMath.sol";

/**
 * @title TriangularArbitrage
 * @dev Advanced triangular arbitrage contract for DAI→USDC→GHO→DAI cycles
 * Supports Balancer weighted pools, Curve StableSwap, and 23bps minimum threshold
 */
contract TriangularArbitrage is 
    FlashLoanSimpleReceiverBase,
    ReentrancyGuard,
    Pausable,
    Ownable
{
    using SafeERC20 for IERC20;
    using BalancerMath for uint256;
    using CurveMath for uint256;
    using SpreadCalculator for uint256;
    using AEONMathUtils for uint256;

    // Base Sepolia testnet token addresses
    address public constant DAI = 0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb;  // DAI on Base Sepolia
    address public constant USDC = 0x036CbD53842c5426634e7929541eC2318f3dCF7e; // USDC on Base Sepolia
    address public constant WETH = 0x4200000000000000000000000000000000000006; // WETH on Base Sepolia
    address public constant GHO = 0x40D16FC0246aD3160Ccc09B8D0D3A2cD28aE6C2f;  // GHO on Base Sepolia (mock)
    
    // DEX interfaces
    address public constant BALANCER_VAULT = 0xBA12222222228d8Ba445958a75a0704d566BF2C8;
    address public constant CURVE_POOL_DAI_USDC = 0x4DEcE678ceceb27446b35C672dC7d61F30bAD69E; // Mock Curve pool
    address public constant CURVE_POOL_USDC_GHO = 0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0; // Mock Curve pool
    
    // Chainlink price feeds (Base Sepolia)
    address public constant DAI_USD_FEED = 0x591e79239a7d679378eC8c847e5038150364C78F;
    address public constant USDC_USD_FEED = 0xd30e2101a97dcbAeBCBC04F14C3f624E67A35165;
    address public constant ETH_USD_FEED = 0xd276FCf34D54A9267738E680a72b7Eaf2E54f2e4;

    // 0x API configuration
    string public constant ZRX_API_URL = "https://api.0x.org/swap/v1/quote";
    
    struct TriangularPath {
        address tokenA;      // Starting token (DAI)
        address tokenB;      // Intermediate token (USDC)
        address tokenC;      // Final token (GHO)
        address poolAB;      // Pool for A→B swap
        address poolBC;      // Pool for B→C swap
        address poolCA;      // Pool for C→A swap
        uint256 amountIn;    // Starting amount
        uint256 minProfitBps; // Minimum profit in basis points (23)
        bool useBalancer;    // Use Balancer for weighted pools
        bool useCurve;       // Use Curve for stable pools
    }

    struct ArbitrageExecution {
        uint256 startAmount;
        uint256 amountAfterAB;
        uint256 amountAfterBC;
        uint256 finalAmount;
        uint256 profit;
        uint256 gasUsed;
        bool successful;
        uint256 timestamp;
        bytes32 txHash;
    }

    // Events
    event TriangularArbitrageExecuted(
        address indexed tokenA,
        address indexed tokenB,
        address indexed tokenC,
        uint256 amountIn,
        uint256 profit,
        uint256 gasUsed,
        bool successful
    );

    event SpreadMonitored(
        address indexed tokenA,
        address indexed tokenB,
        int256 spreadBps,
        uint256 impliedPrice,
        uint256 externalPrice,
        bool isProfitable
    );

    event ProfitWithdrawn(
        address indexed token,
        uint256 amount,
        address indexed recipient
    );

    event ConfigUpdated(
        uint256 maxGasPrice,
        uint256 maxSlippageBps,
        uint256 minProfitUSD
    );

    // State variables
    mapping(bytes32 => ArbitrageExecution) public executions;
    mapping(address => uint256) public tokenProfits;
    uint256 public totalExecutions;
    uint256 public successfulExecutions;
    uint256 public totalProfitUSD;

    // Configuration
    uint256 public maxGasPrice = 50 gwei;
    uint256 public maxSlippageBps = 300; // 3%
    uint256 public minProfitUSD = 10; // $10 minimum profit

    constructor(address _addressProvider) 
        FlashLoanSimpleReceiverBase(IPoolAddressesProvider(_addressProvider))
    {}

    /**
     * @dev Execute triangular arbitrage with flash loan
     * @param path Triangular arbitrage path configuration
     */
    function executeTriangularArbitrage(TriangularPath memory path) 
        external 
        nonReentrant 
        whenNotPaused 
    {
        require(path.amountIn > 0, "TriangularArbitrage: ZERO_AMOUNT");
        require(tx.gasprice <= maxGasPrice, "TriangularArbitrage: GAS_PRICE_TOO_HIGH");

        // Pre-execution checks
        require(_validatePath(path), "TriangularArbitrage: INVALID_PATH");
        require(_checkProfitability(path), "TriangularArbitrage: NOT_PROFITABLE");

        // Encode path data for flash loan callback
        bytes memory params = abi.encode(path);

        // Execute flash loan
        POOL.flashLoanSimple(
            address(this),
            path.tokenA,
            path.amountIn,
            params,
            0 // referralCode
        );
    }

    /**
     * @dev Flash loan callback - executes the triangular arbitrage
     */
    function executeOperation(
        address asset,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata params
    ) external override returns (bool) {
        require(msg.sender == address(POOL), "TriangularArbitrage: INVALID_CALLER");
        require(initiator == address(this), "TriangularArbitrage: INVALID_INITIATOR");

        TriangularPath memory path = abi.decode(params, (TriangularPath));
        
        uint256 startGas = gasleft();
        bool success = _executeTriangularSwaps(path, amount);
        uint256 gasUsed = startGas - gasleft();

        // Calculate final amounts and profit
        uint256 finalBalance = IERC20(asset).balanceOf(address(this));
        uint256 totalDebt = amount + premium;
        
        require(finalBalance >= totalDebt, "TriangularArbitrage: INSUFFICIENT_BALANCE");
        
        uint256 profit = finalBalance - totalDebt;
        
        // Record execution
        _recordExecution(path, amount, profit, gasUsed, success);

        // Approve repayment
        IERC20(asset).safeApprove(address(POOL), totalDebt);

        return true;
    }

    /**
     * @dev Execute the three swaps in the triangular path
     * @param path Triangular path configuration
     * @param startAmount Starting amount from flash loan
     * @return success True if all swaps executed successfully
     */
    function _executeTriangularSwaps(
        TriangularPath memory path,
        uint256 startAmount
    ) internal returns (bool success) {
        try this._performSwapAB(path, startAmount) returns (uint256 amountB) {
            try this._performSwapBC(path, amountB) returns (uint256 amountC) {
                try this._performSwapCA(path, amountC) returns (uint256 finalAmount) {
                    return finalAmount > startAmount;
                } catch {
                    return false;
                }
            } catch {
                return false;
            }
        } catch {
            return false;
        }
    }

    /**
     * @dev Perform A→B swap (DAI→USDC)
     * @param path Triangular path
     * @param amountIn Input amount
     * @return amountOut Output amount
     */
    function _performSwapAB(
        TriangularPath memory path,
        uint256 amountIn
    ) external returns (uint256 amountOut) {
        require(msg.sender == address(this), "TriangularArbitrage: INTERNAL_ONLY");
        
        if (path.useBalancer) {
            amountOut = _swapOnBalancer(path.tokenA, path.tokenB, amountIn, path.poolAB);
        } else if (path.useCurve) {
            amountOut = _swapOnCurve(path.tokenA, path.tokenB, amountIn, path.poolAB);
        } else {
            revert("TriangularArbitrage: NO_DEX_SPECIFIED");
        }
    }

    /**
     * @dev Perform B→C swap (USDC→GHO)
     */
    function _performSwapBC(
        TriangularPath memory path,
        uint256 amountIn
    ) external returns (uint256 amountOut) {
        require(msg.sender == address(this), "TriangularArbitrage: INTERNAL_ONLY");
        
        if (path.useCurve) {
            amountOut = _swapOnCurve(path.tokenB, path.tokenC, amountIn, path.poolBC);
        } else {
            amountOut = _swapOnBalancer(path.tokenB, path.tokenC, amountIn, path.poolBC);
        }
    }

    /**
     * @dev Perform C→A swap (GHO→DAI)
     */
    function _performSwapCA(
        TriangularPath memory path,
        uint256 amountIn
    ) external returns (uint256 amountOut) {
        require(msg.sender == address(this), "TriangularArbitrage: INTERNAL_ONLY");
        
        if (path.useCurve) {
            amountOut = _swapOnCurve(path.tokenC, path.tokenA, amountIn, path.poolCA);
        } else {
            amountOut = _swapOnBalancer(path.tokenC, path.tokenA, amountIn, path.poolCA);
        }
    }

    /**
     * @dev Execute swap on Balancer
     */
    function _swapOnBalancer(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        address pool
    ) internal returns (uint256 amountOut) {
        // Simplified Balancer swap implementation
        // In production, use proper Balancer Vault interface
        IERC20(tokenIn).safeApprove(BALANCER_VAULT, amountIn);
        
        // Mock swap calculation using BalancerMath
        // This would be replaced with actual Balancer Vault calls
        amountOut = amountIn * 99 / 100; // Mock 1% slippage
        
        // Transfer tokens (mock implementation)
        IERC20(tokenIn).safeTransfer(pool, amountIn);
        // In real implementation, tokens would come from Balancer Vault
    }

    /**
     * @dev Execute swap on Curve
     */
    function _swapOnCurve(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        address pool
    ) internal returns (uint256 amountOut) {
        // Simplified Curve swap implementation
        IERC20(tokenIn).safeApprove(pool, amountIn);
        
        // Mock swap calculation using CurveMath
        amountOut = amountIn * 995 / 1000; // Mock 0.5% slippage for stables
        
        // In real implementation, call Curve pool exchange function
    }

    /**
     * @dev Check if triangular arbitrage is profitable with 23bps threshold
     * Uses AEON math library for precise calculations
     */
    function _checkProfitability(TriangularPath memory path)
        internal
        view
        returns (bool isProfitable)
    {
        // Get Chainlink prices for external reference
        (uint256 ethPrice, bool ethStale) = ChainlinkPriceOracle.getETHPrice();
        (uint256 daiPrice, bool daiStale) = ChainlinkPriceOracle.getDAIPrice();
        (uint256 usdcPrice, bool usdcStale) = ChainlinkPriceOracle.getUSDCPrice();

        // Skip if any price is stale
        if (ethStale || daiStale || usdcStale) {
            return false;
        }

        // Calculate implied prices from DEX pools
        uint256 impliedPriceAB = _getImpliedPrice(path.tokenA, path.tokenB, path.poolAB, path.useBalancer);
        uint256 impliedPriceBC = _getImpliedPrice(path.tokenB, path.tokenC, path.poolBC, path.useBalancer);
        uint256 impliedPriceCA = _getImpliedPrice(path.tokenC, path.tokenA, path.poolCA, path.useBalancer);

        // Calculate triangular arbitrage profit using AEON math
        (uint256 profit, bool hasArbitrage) = AEONMath.calculateTriangularProfit(
            impliedPriceAB,
            impliedPriceBC,
            impliedPriceCA,
            path.amountIn
        );

        // Check if profit exceeds minimum threshold
        if (!hasArbitrage) {
            return false;
        }

        // Calculate spread in basis points
        uint256 externalPrice = _getExternalPriceFromOracle(path.tokenA, ethPrice, daiPrice, usdcPrice);
        uint256 finalPrice = (path.amountIn + profit) * 1e18 / path.amountIn;
        int256 spreadBps = AEONMath.calculateSpreadBps(finalPrice, externalPrice);

        // Check 23bps threshold with estimated fees
        uint256 estimatedFeesBps = 15; // ~0.15% estimated total fees (gas + DEX)
        return AEONMath.isAboveThreshold(spreadBps, estimatedFeesBps);
    }

    /**
     * @dev Get implied price from DEX pool using AEON math
     */
    function _getImpliedPrice(
        address tokenA,
        address tokenB,
        address pool,
        bool useBalancer
    ) internal view returns (uint256 impliedPrice) {
        if (useBalancer) {
            // Mock Balancer pool data - in production, query actual pool
            return AEONMath.getBalancerImpliedPrice(
                1000000 * 1e18, // Mock balance A
                2000000 * 1e18, // Mock balance B
                80 * 1e16,       // 80% weight A (0.8)
                20 * 1e16        // 20% weight B (0.2)
            );
        } else {
            // Curve StableSwap - check for depeg using AEON math
            bool isDepegged = AEONMath.detectCurveDepeg(pool, 1e18, 0.02e18); // 2% threshold
            if (isDepegged) {
                return 0; // Skip depegged pools
            }
            return 1e18; // 1:1 for stablecoins
        }
    }

    /**
     * @dev Get external reference price from Chainlink oracles
     */
    function _getExternalPriceFromOracle(
        address token,
        uint256 ethPrice,
        uint256 daiPrice,
        uint256 usdcPrice
    ) internal pure returns (uint256 price) {
        if (token == DAI) return daiPrice * 1e10; // Convert 8 to 18 decimals
        if (token == USDC) return usdcPrice * 1e10;
        if (token == WETH) return ethPrice * 1e10;
        return 1e18; // Default fallback
    }

    /**
     * @dev Get external price from Chainlink or 0x API (legacy function)
     */
    function _getExternalPrice(address tokenA, address tokenB)
        internal
        view
        returns (uint256 price)
    {
        // Simplified price fetching - in production, implement proper price feeds
        if (tokenA == DAI && tokenB == USDC) {
            return 1e18; // 1:1 for stablecoins
        } else if (tokenA == USDC && tokenB == GHO) {
            return 1e18; // 1:1 for stablecoins
        } else if (tokenA == GHO && tokenB == DAI) {
            return 1e18; // 1:1 for stablecoins
        }
        return 1e18; // Default 1:1
    }

    /**
     * @dev Validate triangular path parameters
     */
    function _validatePath(TriangularPath memory path) internal pure returns (bool) {
        return (
            path.tokenA != address(0) &&
            path.tokenB != address(0) &&
            path.tokenC != address(0) &&
            path.amountIn > 0 &&
            path.minProfitBps >= SpreadCalculator.MIN_SPREAD_BPS
        );
    }

    /**
     * @dev Record arbitrage execution
     */
    function _recordExecution(
        TriangularPath memory path,
        uint256 startAmount,
        uint256 profit,
        uint256 gasUsed,
        bool successful
    ) internal {
        bytes32 executionId = keccak256(abi.encodePacked(
            block.timestamp,
            path.tokenA,
            path.tokenB,
            path.tokenC,
            startAmount
        ));

        executions[executionId] = ArbitrageExecution({
            startAmount: startAmount,
            amountAfterAB: 0, // Would be tracked in real implementation
            amountAfterBC: 0,
            finalAmount: startAmount + profit,
            profit: profit,
            gasUsed: gasUsed,
            successful: successful,
            timestamp: block.timestamp,
            txHash: blockhash(block.number - 1)
        });

        totalExecutions++;
        if (successful) {
            successfulExecutions++;
            tokenProfits[path.tokenA] += profit;
        }

        emit TriangularArbitrageExecuted(
            path.tokenA,
            path.tokenB,
            path.tokenC,
            startAmount,
            profit,
            gasUsed,
            successful
        );
    }

    /**
     * @dev Withdraw accumulated profits (owner only)
     */
    function withdrawProfits(address token, uint256 amount) 
        external 
        onlyOwner 
    {
        require(amount <= tokenProfits[token], "TriangularArbitrage: INSUFFICIENT_PROFIT");
        
        tokenProfits[token] -= amount;
        IERC20(token).safeTransfer(owner(), amount);
        
        emit ProfitWithdrawn(token, amount, owner());
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
     * @dev Execute triangular arbitrage with enhanced AEON math and 23bps threshold
     * @param tokenA First token (start/end)
     * @param tokenB Second token (intermediate)
     * @param tokenC Third token (intermediate)
     * @param amount Input amount
     */
    function executeTriangularArbitrageWithAEON(
        address tokenA,
        address tokenB,
        address tokenC,
        uint256 amount
    ) external onlyOwner nonReentrant whenNotPaused {
        require(amount > 0, "TriangularArbitrage: ZERO_AMOUNT");
        require(tx.gasprice <= maxGasPrice, "TriangularArbitrage: GAS_PRICE_TOO_HIGH");

        // Create path with AEON optimizations
        TriangularPath memory path = TriangularPath({
            tokenA: tokenA,
            tokenB: tokenB,
            tokenC: tokenC,
            poolAB: _getOptimalPool(tokenA, tokenB),
            poolBC: _getOptimalPool(tokenB, tokenC),
            poolCA: _getOptimalPool(tokenC, tokenA),
            amountIn: amount,
            minProfitBps: 23, // 23bps minimum threshold
            useBalancer: _shouldUseBalancer(tokenA, tokenB),
            useCurve: _shouldUseCurve(tokenA, tokenB)
        });

        // Enhanced profitability check with AEON math
        require(_checkProfitability(path), "TriangularArbitrage: NOT_PROFITABLE");

        // Execute arbitrage
        _executeTriangularSwaps(path);

        emit TriangularArbitrageExecuted(tokenA, tokenB, tokenC, amount, 0, gasleft(), true);
    }

    /**
     * @dev Get optimal pool for token pair
     */
    function _getOptimalPool(address tokenA, address tokenB) internal pure returns (address) {
        // Mock pool selection - in production, query actual pools
        if ((tokenA == DAI && tokenB == USDC) || (tokenA == USDC && tokenB == DAI)) {
            return 0x4DEcE678ceceb27446b35C672dC7d61F30bAD69E; // Curve DAI/USDC
        } else if ((tokenA == USDC && tokenB == GHO) || (tokenA == GHO && tokenB == USDC)) {
            return 0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0; // Curve USDC/GHO
        } else {
            return 0xBA12222222228d8Ba445958a75a0704d566BF2C8; // Balancer Vault
        }
    }

    /**
     * @dev Determine if should use Balancer for token pair
     */
    function _shouldUseBalancer(address tokenA, address tokenB) internal pure returns (bool) {
        // Use Balancer for volatile pairs (WETH involved)
        return (tokenA == WETH || tokenB == WETH);
    }

    /**
     * @dev Determine if should use Curve for token pair
     */
    function _shouldUseCurve(address tokenA, address tokenB) internal pure returns (bool) {
        // Use Curve for stablecoin pairs
        return (tokenA == DAI || tokenA == USDC || tokenA == GHO) &&
               (tokenB == DAI || tokenB == USDC || tokenB == GHO);
    }

    /**
     * @dev Execute the actual triangular swaps with 23bps verification
     */
    function _executeTriangularSwaps(TriangularPath memory path) internal {
        uint256 startBalance = IERC20(path.tokenA).balanceOf(address(this));

        // A → B
        uint256 amountB = _performSwap(path.tokenA, path.tokenB, path.amountIn, path.poolAB, path.useBalancer);

        // B → C
        uint256 amountC = _performSwap(path.tokenB, path.tokenC, amountB, path.poolBC, path.useBalancer);

        // C → A
        uint256 finalAmount = _performSwap(path.tokenC, path.tokenA, amountC, path.poolCA, path.useBalancer);

        // Verify profit exceeds 23bps threshold
        require(finalAmount > startBalance, "TriangularArbitrage: NO_PROFIT");

        uint256 profit = finalAmount - startBalance;
        uint256 profitBps = (profit * 10000) / startBalance;
        require(profitBps >= 23, "TriangularArbitrage: INSUFFICIENT_PROFIT");
    }

    /**
     * @dev Perform individual swap with DEX selection
     */
    function _performSwap(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        address pool,
        bool useBalancer
    ) internal returns (uint256 amountOut) {
        if (useBalancer) {
            return _swapOnBalancer(tokenIn, tokenOut, amountIn, pool);
        } else {
            return _swapOnCurve(tokenIn, tokenOut, amountIn, pool);
        }
    }

    /**
     * @dev Update configuration parameters
     */
    function updateConfig(
        uint256 _maxGasPrice,
        uint256 _maxSlippageBps,
        uint256 _minProfitUSD
    ) external onlyOwner {
        maxGasPrice = _maxGasPrice;
        maxSlippageBps = _maxSlippageBps;
        minProfitUSD = _minProfitUSD;

        emit ConfigUpdated(_maxGasPrice, _maxSlippageBps, _minProfitUSD);
    }
}

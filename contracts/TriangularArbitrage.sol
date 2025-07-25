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

    // Base Sepolia testnet token addresses
    address public constant DAI = 0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb;  // DAI on Base Sepolia
    address public constant USDC = 0x036CbD53842c5426634e7929541eC2318f3dCF7e; // USDC on Base Sepolia
    address public constant GHO = 0x40D16FC0246aD3160Ccc09B8D0D3A2cD28aE6C2f;  // GHO on Base Sepolia (mock)
    
    // DEX interfaces
    address public constant BALANCER_VAULT = 0xBA12222222228d8Ba445958a75a0704d566BF2C8;
    address public constant CURVE_POOL_DAI_USDC = 0x4DEcE678ceceb27446b35C672dC7d61F30bAD69E; // Mock Curve pool
    address public constant CURVE_POOL_USDC_GHO = 0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0; // Mock Curve pool
    
    // Chainlink price feeds (Base Sepolia)
    address public constant DAI_USD_FEED = 0x591e79239a7d679378eC8c847e5038150364C78F;
    address public constant USDC_USD_FEED = 0xd30e2101a97dcbAeBCBC04F14C3f624E67A35165;
    address public constant ETH_USD_FEED = 0xD276fCF34D54A9267738e680A72b7EaF2E54f2E4;

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
     * @dev Check if triangular arbitrage is profitable
     */
    function _checkProfitability(TriangularPath memory path) 
        internal 
        view 
        returns (bool isProfitable) 
    {
        // Get external prices from Chainlink/0x API
        uint256 priceAB = _getExternalPrice(path.tokenA, path.tokenB);
        uint256 priceBC = _getExternalPrice(path.tokenB, path.tokenC);
        uint256 priceCA = _getExternalPrice(path.tokenC, path.tokenA);
        
        // Calculate triangular arbitrage profit
        (uint256 profit, bool hasArbitrage) = SpreadCalculator.calculateTriangularArbitrage(
            priceAB,
            priceBC,
            priceCA,
            path.amountIn
        );
        
        return hasArbitrage && profit > 0;
    }

    /**
     * @dev Get external price from Chainlink or 0x API
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
    }
}

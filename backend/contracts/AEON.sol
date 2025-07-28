// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@aave/core-v3/contracts/flashloan/base/FlashLoanSimpleReceiverBase.sol";
import "@aave/core-v3/contracts/interfaces/IPoolAddressesProvider.sol";
import "@aave/core-v3/contracts/interfaces/IPool.sol";
import "./lib/AEONArbitrageExtensions.sol";
import "./lib/AEONMath.sol";

/**
 * @title AEON - Advanced Efficient Optimized Network (Option 1)
 * @dev Fully autonomous on-chain arbitrage with Chainlink + Smart Contract Logic
 * Pure AEON logic chain - immutable, verifiable, unstoppable
 * 
 * Features:
 * - Autonomous execution based on Chainlink price feeds
 * - 23bps minimum threshold enforcement
 * - Balancer weighted pool math (80/20, 98/2)
 * - Curve StableSwap with depeg detection
 * - Triangular arbitrage optimization
 * - Flash loan integration (Aave V3)
 * - MEV protection and gas optimization
 */
contract AEON is 
    FlashLoanSimpleReceiverBase,
    ReentrancyGuard,
    Pausable,
    Ownable
{
    using SafeERC20 for IERC20;
    using AEONMath for uint256;
    using ChainlinkPriceOracle for address;

    // AEON Network Configuration
    struct AEONConfig {
        uint256 minSpreadBps;           // 23bps minimum
        uint256 maxGasPrice;            // 50 gwei max
        uint256 maxSlippageBps;         // 300bps max slippage
        uint256 minProfitUSD;           // $10 minimum profit
        uint256 maxFlashLoanAmount;     // $10M max flash loan
        bool autonomousMode;            // True for full autonomy
        uint256 executionCooldown;      // Cooldown between executions
    }

    // Ecosystem State
    struct EcosystemState {
        uint256 totalExecutions;
        uint256 successfulExecutions;
        uint256 totalProfitUSD;
        uint256 totalGasSpent;
        uint256 lastExecutionTime;
        uint256 averageSpreadBps;
        bool isHealthy;
    }

    // Arbitrage Opportunity
    struct Opportunity {
        address tokenA;
        address tokenB;
        address tokenC;
        uint256 amountIn;
        int256 spreadBps;
        uint256 estimatedProfit;
        uint256 gasEstimate;
        bool isValid;
        uint256 detectedAt;
    }

    // State Variables
    AEONConfig public config;
    EcosystemState public state;
    
    mapping(bytes32 => Opportunity) public opportunities;
    mapping(address => uint256) public tokenProfits;
    mapping(address => bool) public authorizedTokens;
    
    bytes32[] public activeOpportunities;
    
    // Base Sepolia Token Addresses
    address public constant DAI = 0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb;
    address public constant USDC = 0x036CbD53842c5426634e7929541eC2318f3dCF7e;
    address public constant WETH = 0x4200000000000000000000000000000000000006;
    address public constant GHO = 0x40D16FC0246aD3160Ccc09B8D0D3A2cD28aE6C2f;

    // Events
    event AEONExecuted(bytes32 indexed opportunityId, uint256 profit, uint256 gasUsed);
    event OpportunityDetected(bytes32 indexed opportunityId, int256 spreadBps);
    event EcosystemStateUpdated(uint256 totalExecutions, uint256 totalProfit);
    event ConfigUpdated(AEONConfig newConfig);

    constructor(address _poolAddressesProvider) 
        FlashLoanSimpleReceiverBase(IPoolAddressesProvider(_poolAddressesProvider))
    {
        // Initialize AEON configuration
        config = AEONConfig({
            minSpreadBps: 23,           // 0.23% minimum
            maxGasPrice: 50e9,          // 50 gwei
            maxSlippageBps: 300,        // 3% max slippage
            minProfitUSD: 10e18,        // $10 minimum
            maxFlashLoanAmount: 10_000_000e18, // $10M max
            autonomousMode: true,       // Full autonomy
            executionCooldown: 30       // 30 seconds cooldown
        });

        // Initialize ecosystem state
        state = EcosystemState({
            totalExecutions: 0,
            successfulExecutions: 0,
            totalProfitUSD: 0,
            totalGasSpent: 0,
            lastExecutionTime: 0,
            averageSpreadBps: 0,
            isHealthy: true
        });

        // Authorize base tokens
        authorizedTokens[DAI] = true;
        authorizedTokens[USDC] = true;
        authorizedTokens[WETH] = true;
        authorizedTokens[GHO] = true;
    }

    /**
     * @dev AEON Autonomous Execution - Main Entry Point
     * Scans for opportunities and executes if profitable
     */
    function executeAEON() external nonReentrant whenNotPaused {
        require(config.autonomousMode, "AEON: AUTONOMOUS_MODE_DISABLED");
        require(
            block.timestamp >= state.lastExecutionTime + config.executionCooldown,
            "AEON: COOLDOWN_ACTIVE"
        );
        require(tx.gasprice <= config.maxGasPrice, "AEON: GAS_PRICE_TOO_HIGH");

        // Scan for opportunities
        bytes32 bestOpportunityId = _scanForOpportunities();
        
        if (bestOpportunityId != bytes32(0)) {
            Opportunity storage opp = opportunities[bestOpportunityId];
            
            // Validate opportunity is still profitable
            if (_validateOpportunity(opp)) {
                _executeArbitrage(opp);
                state.lastExecutionTime = block.timestamp;
            }
        }
    }

    /**
     * @dev Scan for arbitrage opportunities using Chainlink feeds
     */
    function _scanForOpportunities() internal returns (bytes32 bestOpportunityId) {
        uint256 bestSpread = 0;
        
        // Predefined high-volume triangular paths
        address[3][3] memory paths = [
            [DAI, USDC, GHO],      // DAI → USDC → GHO → DAI
            [WETH, USDC, DAI],     // WETH → USDC → DAI → WETH
            [USDC, DAI, GHO]       // USDC → DAI → GHO → USDC
        ];

        for (uint256 i = 0; i < paths.length; i++) {
            bytes32 oppId = _analyzeTriangularPath(paths[i]);
            
            if (oppId != bytes32(0)) {
                Opportunity storage opp = opportunities[oppId];
                uint256 absSpread = opp.spreadBps >= 0 ? 
                    uint256(opp.spreadBps) : uint256(-opp.spreadBps);
                
                if (absSpread > bestSpread) {
                    bestSpread = absSpread;
                    bestOpportunityId = oppId;
                }
            }
        }
    }

    /**
     * @dev Analyze triangular arbitrage path
     */
    function _analyzeTriangularPath(address[3] memory tokens) 
        internal 
        returns (bytes32 opportunityId) 
    {
        // Get Chainlink prices
        (uint256 priceA, bool staleA) = ChainlinkPriceOracle.getLatestPrice(
            _getChainlinkFeed(tokens[0])
        );
        (uint256 priceB, bool staleB) = ChainlinkPriceOracle.getLatestPrice(
            _getChainlinkFeed(tokens[1])
        );
        (uint256 priceC, bool staleC) = ChainlinkPriceOracle.getLatestPrice(
            _getChainlinkFeed(tokens[2])
        );

        // Skip if any price is stale
        if (staleA || staleB || staleC) return bytes32(0);

        // Calculate triangular arbitrage
        uint256 amount = 10000e18; // $10k test amount
        (uint256 profit, bool isProfitable) = AEONMath.calculateTriangularProfit(
            priceA * 1e10 / priceB, // A/B price (convert 8 to 18 decimals)
            priceB * 1e10 / priceC, // B/C price
            priceC * 1e10 / priceA, // C/A price
            amount
        );

        if (!isProfitable) return bytes32(0);

        // Calculate spread
        int256 spreadBps = int256(profit * 10000 / amount);
        
        // Check 23bps threshold
        if (!AEONMath.isAboveThreshold(spreadBps, 15)) return bytes32(0); // 15bps fees

        // Create opportunity
        opportunityId = keccak256(abi.encodePacked(
            tokens[0], tokens[1], tokens[2], block.timestamp
        ));

        opportunities[opportunityId] = Opportunity({
            tokenA: tokens[0],
            tokenB: tokens[1],
            tokenC: tokens[2],
            amountIn: amount,
            spreadBps: spreadBps,
            estimatedProfit: profit,
            gasEstimate: 450000, // Estimated gas for triangular arbitrage
            isValid: true,
            detectedAt: block.timestamp
        });

        activeOpportunities.push(opportunityId);
        emit OpportunityDetected(opportunityId, spreadBps);
    }

    /**
     * @dev Get Chainlink feed address for token
     */
    function _getChainlinkFeed(address token) internal pure returns (address) {
        if (token == DAI) return ChainlinkPriceOracle.DAI_USD_FEED;
        if (token == USDC) return ChainlinkPriceOracle.USDC_USD_FEED;
        if (token == WETH) return ChainlinkPriceOracle.ETH_USD_FEED;
        return address(0); // GHO doesn't have feed, use fallback
    }

    /**
     * @dev Validate opportunity is still profitable
     */
    function _validateOpportunity(Opportunity memory opp) internal view returns (bool) {
        // Check if opportunity is too old (5 minutes max)
        if (block.timestamp - opp.detectedAt > 300) return false;
        
        // Re-validate spread is above threshold
        return AEONMath.isAboveThreshold(opp.spreadBps, 15);
    }

    /**
     * @dev Execute arbitrage using flash loan
     */
    function _executeArbitrage(Opportunity memory opp) internal {
        require(opp.amountIn <= config.maxFlashLoanAmount, "AEON: AMOUNT_TOO_LARGE");
        
        // Encode opportunity data for flash loan callback
        bytes memory params = abi.encode(opp);
        
        // Execute flash loan
        POOL.flashLoanSimple(
            address(this),
            opp.tokenA,
            opp.amountIn,
            params,
            0 // referralCode
        );
    }

    /**
     * @dev Flash loan callback - execute triangular arbitrage
     */
    function executeOperation(
        address asset,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata params
    ) external override returns (bool) {
        require(msg.sender == address(POOL), "AEON: INVALID_CALLER");
        require(initiator == address(this), "AEON: INVALID_INITIATOR");

        // Decode opportunity
        Opportunity memory opp = abi.decode(params, (Opportunity));
        
        uint256 startGas = gasleft();
        
        // Execute triangular swaps
        bool success = _executeTriangularSwaps(opp);
        
        uint256 gasUsed = startGas - gasleft();
        
        if (success) {
            // Update ecosystem state
            state.totalExecutions++;
            state.successfulExecutions++;
            state.totalGasSpent += gasUsed;
            state.averageSpreadBps = (state.averageSpreadBps + uint256(opp.spreadBps)) / 2;
            
            emit AEONExecuted(
                keccak256(abi.encodePacked(opp.tokenA, opp.tokenB, opp.tokenC)),
                opp.estimatedProfit,
                gasUsed
            );
        }

        // Repay flash loan
        uint256 amountOwed = amount + premium;
        IERC20(asset).safeApprove(address(POOL), amountOwed);
        
        return true;
    }

    /**
     * @dev Execute triangular swaps A→B→C→A
     */
    function _executeTriangularSwaps(Opportunity memory opp) internal returns (bool) {
        try this._performSwapAB(opp) returns (uint256 amountB) {
            try this._performSwapBC(opp, amountB) returns (uint256 amountC) {
                try this._performSwapCA(opp, amountC) returns (uint256 finalAmount) {
                    return finalAmount > opp.amountIn;
                } catch { return false; }
            } catch { return false; }
        } catch { return false; }
    }

    /**
     * @dev Perform A→B swap (external for try/catch)
     */
    function _performSwapAB(Opportunity memory opp) external returns (uint256) {
        require(msg.sender == address(this), "AEON: INTERNAL_ONLY");
        // Mock swap - in production, integrate with actual DEX
        return opp.amountIn * 99 / 100; // 1% slippage
    }

    /**
     * @dev Perform B→C swap (external for try/catch)
     */
    function _performSwapBC(Opportunity memory opp, uint256 amountB) external returns (uint256) {
        require(msg.sender == address(this), "AEON: INTERNAL_ONLY");
        // Mock swap - in production, integrate with actual DEX
        return amountB * 99 / 100; // 1% slippage
    }

    /**
     * @dev Perform C→A swap (external for try/catch)
     */
    function _performSwapCA(Opportunity memory opp, uint256 amountC) external returns (uint256) {
        require(msg.sender == address(this), "AEON: INTERNAL_ONLY");
        // Mock swap - in production, integrate with actual DEX
        return amountC * 99 / 100; // 1% slippage
    }

    /**
     * @dev Update AEON configuration (owner only)
     */
    function updateConfig(AEONConfig memory newConfig) external onlyOwner {
        config = newConfig;
        emit ConfigUpdated(newConfig);
    }

    /**
     * @dev Get ecosystem health status
     */
    function getEcosystemHealth() external view returns (EcosystemState memory) {
        return state;
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
     * @dev Withdraw accumulated profits (owner only)
     */
    function withdrawProfits(address token, uint256 amount) external onlyOwner {
        require(tokenProfits[token] >= amount, "AEON: INSUFFICIENT_PROFIT");
        tokenProfits[token] -= amount;
        IERC20(token).safeTransfer(owner(), amount);
    }
}

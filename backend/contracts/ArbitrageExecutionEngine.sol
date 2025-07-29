// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "./TriangularArbitrage.sol";
import "./PriceMonitor.sol";
import "./libraries/SpreadCalculator.sol";
import "./lib/AEONArbitrageExtensions.sol";

/**
 * @title ArbitrageExecutionEngine
 * @dev Automated execution system for high-volatility token pairs with profit optimization
 * Manages pre-set triangular arbitrage paths and executes when profitable
 */
contract ArbitrageExecutionEngine is ReentrancyGuard, Pausable, Ownable {
    using SafeERC20 for IERC20;
    using SpreadCalculator for uint256;
    using AEONMath for uint256;

    // Core contracts
    TriangularArbitrage public immutable triangularArbitrage;
    PriceMonitor public immutable priceMonitor;

    // High-volatility token pairs for arbitrage
    struct TokenTriple {
        address tokenA;
        address tokenB;
        address tokenC;
        string name;
        uint256 priority; // 1 = highest priority
        bool isActive;
        uint256 minAmount;
        uint256 maxAmount;
        uint256 lastExecuted;
        uint256 totalExecutions;
        uint256 totalProfit;
    }

    struct ExecutionStrategy {
        uint256 maxGasPrice;
        uint256 maxSlippageBps;
        uint256 minProfitBps;
        uint256 maxTradeSize;
        uint256 cooldownPeriod;
        bool autoExecute;
        uint256 riskLevel; // 1 = conservative, 5 = aggressive
    }

    struct ArbitrageExecution {
        bytes32 tripleId;
        uint256 amountIn;
        uint256 profit;
        uint256 gasUsed;
        uint256 timestamp;
        bool successful;
        string failureReason;
    }

    // Pre-configured high-volatility triangular paths
    mapping(bytes32 => TokenTriple) public tokenTriples;
    bytes32[] public activeTripleIds;
    
    // Execution strategies per triple
    mapping(bytes32 => ExecutionStrategy) public strategies;
    
    // Execution history
    mapping(bytes32 => ArbitrageExecution[]) public executionHistory;
    
    // Performance metrics
    mapping(bytes32 => uint256) public profitability; // Profit per execution
    mapping(bytes32 => uint256) public successRate; // Success rate in basis points
    
    // Events
    event TripleAdded(bytes32 indexed tripleId, string name, address tokenA, address tokenB, address tokenC);
    event ArbitrageExecuted(bytes32 indexed tripleId, uint256 amountIn, uint256 profit, bool successful);
    event StrategyUpdated(bytes32 indexed tripleId, ExecutionStrategy strategy);
    event AutoExecutionToggled(bytes32 indexed tripleId, bool enabled);

    // Configuration
    uint256 public constant MAX_TRIPLES = 50;
    uint256 public constant MIN_EXECUTION_INTERVAL = 60; // 1 minute
    uint256 public executionNonce;
    
    // Circuit breaker
    uint256 public maxDailyLoss = 1000 ether; // $1000 max daily loss
    uint256 public dailyLossTracker;
    uint256 public lastResetDay;

    constructor(
        address _triangularArbitrage,
        address _priceMonitor
    ) {
        triangularArbitrage = TriangularArbitrage(_triangularArbitrage);
        priceMonitor = PriceMonitor(_priceMonitor);
        
        _initializeHighVolatilityPairs();
    }

    /**
     * @dev Initialize pre-set high-volatility token triples
     */
    function _initializeHighVolatilityPairs() internal {
        // DAI → USDC → GHO → DAI (Stablecoin arbitrage)
        _addTokenTriple(
            "DAI-USDC-GHO",
            0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb, // DAI
            0x036CbD53842c5426634e7929541eC2318f3dCF7e, // USDC
            0x40D16FC0246aD3160Ccc09B8D0D3A2cD28aE6C2f, // GHO
            1, // Highest priority
            100 ether, // Min $100
            10000 ether // Max $10,000
        );

        // WETH → USDC → WBTC → WETH (Volatile crypto arbitrage)
        _addTokenTriple(
            "WETH-USDC-WBTC",
            0x4200000000000000000000000000000000000006, // WETH
            0x036CbD53842c5426634e7929541eC2318f3dCF7e, // USDC
            0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6, // WBTC (mock)
            2, // High priority
            50 ether, // Min $50
            5000 ether // Max $5,000
        );

        // USDT → DAI → GHO → USDT (Alternative stablecoin path)
        _addTokenTriple(
            "USDT-DAI-GHO",
            0xdAC17F958D2ee523a2206206994597C13D831ec7, // USDT (mock)
            0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb, // DAI
            0x40D16FC0246aD3160Ccc09B8D0D3A2cD28aE6C2f, // GHO
            3, // Medium priority
            200 ether, // Min $200
            8000 ether // Max $8,000
        );
    }

    /**
     * @dev Add a new token triple for arbitrage
     */
    function _addTokenTriple(
        string memory name,
        address tokenA,
        address tokenB,
        address tokenC,
        uint256 priority,
        uint256 minAmount,
        uint256 maxAmount
    ) internal {
        bytes32 tripleId = keccak256(abi.encodePacked(tokenA, tokenB, tokenC));
        
        tokenTriples[tripleId] = TokenTriple({
            tokenA: tokenA,
            tokenB: tokenB,
            tokenC: tokenC,
            name: name,
            priority: priority,
            isActive: true,
            minAmount: minAmount,
            maxAmount: maxAmount,
            lastExecuted: 0,
            totalExecutions: 0,
            totalProfit: 0
        });

        // Set default strategy
        strategies[tripleId] = ExecutionStrategy({
            maxGasPrice: 50 gwei,
            maxSlippageBps: 300, // 3%
            minProfitBps: 23, // 0.23%
            maxTradeSize: maxAmount,
            cooldownPeriod: 300, // 5 minutes
            autoExecute: true,
            riskLevel: 3 // Moderate risk
        });

        activeTripleIds.push(tripleId);
        
        emit TripleAdded(tripleId, name, tokenA, tokenB, tokenC);
    }

    /**
     * @dev Scan all active triples for arbitrage opportunities
     * @return opportunities Array of profitable opportunities
     */
    function scanArbitrageOpportunities() 
        external 
        view 
        returns (bytes32[] memory opportunities, uint256[] memory expectedProfits) 
    {
        uint256 count = 0;
        bytes32[] memory tempOpportunities = new bytes32[](activeTripleIds.length);
        uint256[] memory tempProfits = new uint256[](activeTripleIds.length);

        for (uint256 i = 0; i < activeTripleIds.length; i++) {
            bytes32 tripleId = activeTripleIds[i];
            TokenTriple memory triple = tokenTriples[tripleId];
            
            if (!triple.isActive) continue;
            
            // Check if cooldown period has passed
            if (block.timestamp < triple.lastExecuted + strategies[tripleId].cooldownPeriod) {
                continue;
            }

            // Calculate potential profit
            uint256 profit = _calculateTriangularProfit(tripleId, triple.minAmount);
            
            if (profit > 0) {
                tempOpportunities[count] = tripleId;
                tempProfits[count] = profit;
                count++;
            }
        }

        // Resize arrays to actual count
        opportunities = new bytes32[](count);
        expectedProfits = new uint256[](count);
        
        for (uint256 i = 0; i < count; i++) {
            opportunities[i] = tempOpportunities[i];
            expectedProfits[i] = tempProfits[i];
        }
    }

    /**
     * @dev Execute arbitrage for a specific token triple
     * @param tripleId Token triple identifier
     * @param amount Trade amount
     */
    function executeArbitrage(bytes32 tripleId, uint256 amount) 
        external 
        nonReentrant 
        whenNotPaused 
    {
        TokenTriple storage triple = tokenTriples[tripleId];
        require(triple.isActive, "ArbitrageEngine: TRIPLE_INACTIVE");
        require(amount >= triple.minAmount && amount <= triple.maxAmount, "ArbitrageEngine: INVALID_AMOUNT");
        
        ExecutionStrategy memory strategy = strategies[tripleId];
        require(tx.gasprice <= strategy.maxGasPrice, "ArbitrageEngine: GAS_TOO_HIGH");
        
        // Check cooldown
        require(
            block.timestamp >= triple.lastExecuted + strategy.cooldownPeriod,
            "ArbitrageEngine: COOLDOWN_ACTIVE"
        );

        // Check daily loss limit
        _checkDailyLossLimit();

        // Enhanced profitability check with AEON math
        require(_shouldExecuteWithAEONMath(tripleId, amount, strategy), "ArbitrageEngine: AEON_CHECK_FAILED");

        // Calculate expected profit
        uint256 expectedProfit = _calculateTriangularProfit(tripleId, amount);
        require(expectedProfit > 0, "ArbitrageEngine: NOT_PROFITABLE");

        // Execute triangular arbitrage
        uint256 startGas = gasleft();
        bool success = _executeTriangularArbitrage(tripleId, amount);
        uint256 gasUsed = startGas - gasleft();

        // Record execution
        _recordExecution(tripleId, amount, expectedProfit, gasUsed, success);
        
        // Update triple stats
        triple.lastExecuted = block.timestamp;
        triple.totalExecutions++;
        
        if (success) {
            triple.totalProfit += expectedProfit;
        }

        emit ArbitrageExecuted(tripleId, amount, expectedProfit, success);
    }

    /**
     * @dev Auto-execute arbitrage for all profitable opportunities
     * @return executedCount Number of arbitrages executed
     */
    function autoExecuteArbitrage() 
        external 
        nonReentrant 
        whenNotPaused 
        returns (uint256 executedCount) 
    {
        (bytes32[] memory opportunities, uint256[] memory profits) = this.scanArbitrageOpportunities();
        
        // Sort by profitability (highest first)
        _sortOpportunitiesByProfit(opportunities, profits);
        
        for (uint256 i = 0; i < opportunities.length && i < 5; i++) { // Max 5 per call
            bytes32 tripleId = opportunities[i];
            TokenTriple memory triple = tokenTriples[tripleId];
            ExecutionStrategy memory strategy = strategies[tripleId];
            
            if (!strategy.autoExecute) continue;

            // Calculate optimal trade size
            uint256 optimalSize = _calculateOptimalTradeSize(tripleId, profits[i]);

            if (optimalSize >= triple.minAmount) {
                // Pre-check with AEON math before execution
                if (_shouldExecuteWithAEONMath(tripleId, optimalSize, strategy)) {
                    try this.executeArbitrage(tripleId, optimalSize) {
                        executedCount++;
                    } catch {
                        // Continue to next opportunity if execution fails
                        continue;
                    }
                }
            }
        }
    }

    /**
     * @dev Calculate triangular arbitrage profit for a triple
     */
    function _calculateTriangularProfit(bytes32 tripleId, uint256 amount) 
        internal 
        view 
        returns (uint256 profit) 
    {
        TokenTriple memory triple = tokenTriples[tripleId];
        
        // Get prices from PriceMonitor
        // This is simplified - in production, would get actual DEX prices
        try priceMonitor.getChainlinkPrice(triple.tokenA) returns (uint256 priceA, bool staleA) {
            try priceMonitor.getChainlinkPrice(triple.tokenB) returns (uint256 priceB, bool staleB) {
                try priceMonitor.getChainlinkPrice(triple.tokenC) returns (uint256 priceC, bool staleC) {
                    if (!staleA && !staleB && !staleC) {
                        // Calculate triangular arbitrage profit
                        (uint256 calculatedProfit, bool isArbitrage) = SpreadCalculator.calculateTriangularArbitrage(
                            priceA * 1e18 / priceB, // A/B price
                            priceB * 1e18 / priceC, // B/C price
                            priceC * 1e18 / priceA, // C/A price
                            amount
                        );
                        
                        if (isArbitrage) {
                            profit = calculatedProfit;
                        }
                    }
                } catch {}
            } catch {}
        } catch {}
    }

    /**
     * @dev Execute triangular arbitrage through TriangularArbitrage contract
     */
    function _executeTriangularArbitrage(bytes32 tripleId, uint256 amount) 
        internal 
        returns (bool success) 
    {
        TokenTriple memory triple = tokenTriples[tripleId];
        
        // Create triangular path
        TriangularArbitrage.TriangularPath memory path = TriangularArbitrage.TriangularPath({
            tokenA: triple.tokenA,
            tokenB: triple.tokenB,
            tokenC: triple.tokenC,
            poolAB: address(0), // Would be set based on DEX routing
            poolBC: address(0),
            poolCA: address(0),
            amountIn: amount,
            minProfitBps: strategies[tripleId].minProfitBps,
            useBalancer: false,
            useCurve: true
        });

        try triangularArbitrage.executeTriangularArbitrage(path) {
            success = true;
        } catch {
            success = false;
        }
    }

    /**
     * @dev Calculate optimal trade size based on profit and risk
     */
    function _calculateOptimalTradeSize(bytes32 tripleId, uint256 expectedProfit) 
        internal 
        view 
        returns (uint256 optimalSize) 
    {
        TokenTriple memory triple = tokenTriples[tripleId];
        ExecutionStrategy memory strategy = strategies[tripleId];
        
        // Base size on expected profit and risk level
        uint256 baseSize = triple.minAmount;
        
        if (expectedProfit > 0) {
            // Increase size based on profitability, capped by risk level
            uint256 multiplier = (strategy.riskLevel * expectedProfit) / (triple.minAmount / 10);
            optimalSize = baseSize * (1 + multiplier / 100);
            
            // Cap at max trade size
            if (optimalSize > strategy.maxTradeSize) {
                optimalSize = strategy.maxTradeSize;
            }
        } else {
            optimalSize = baseSize;
        }
    }

    /**
     * @dev Record arbitrage execution
     */
    function _recordExecution(
        bytes32 tripleId,
        uint256 amount,
        uint256 profit,
        uint256 gasUsed,
        bool success
    ) internal {
        executionHistory[tripleId].push(ArbitrageExecution({
            tripleId: tripleId,
            amountIn: amount,
            profit: success ? profit : 0,
            gasUsed: gasUsed,
            timestamp: block.timestamp,
            successful: success,
            failureReason: success ? "" : "Execution failed"
        }));

        executionNonce++;
    }

    /**
     * @dev Sort opportunities by profit (descending)
     */
    function _sortOpportunitiesByProfit(
        bytes32[] memory opportunities,
        uint256[] memory profits
    ) internal pure {
        for (uint256 i = 0; i < opportunities.length - 1; i++) {
            for (uint256 j = 0; j < opportunities.length - i - 1; j++) {
                if (profits[j] < profits[j + 1]) {
                    // Swap profits
                    uint256 tempProfit = profits[j];
                    profits[j] = profits[j + 1];
                    profits[j + 1] = tempProfit;
                    
                    // Swap opportunities
                    bytes32 tempOpp = opportunities[j];
                    opportunities[j] = opportunities[j + 1];
                    opportunities[j + 1] = tempOpp;
                }
            }
        }
    }

    /**
     * @dev Check daily loss limit circuit breaker
     */
    function _checkDailyLossLimit() internal {
        uint256 currentDay = block.timestamp / 86400;
        
        if (currentDay > lastResetDay) {
            dailyLossTracker = 0;
            lastResetDay = currentDay;
        }
        
        require(dailyLossTracker < maxDailyLoss, "ArbitrageEngine: DAILY_LOSS_LIMIT");
    }

    /**
     * @dev Update execution strategy for a triple
     */
    function updateStrategy(bytes32 tripleId, ExecutionStrategy calldata newStrategy) 
        external 
        onlyOwner 
    {
        require(tokenTriples[tripleId].tokenA != address(0), "ArbitrageEngine: TRIPLE_NOT_FOUND");
        strategies[tripleId] = newStrategy;
        emit StrategyUpdated(tripleId, newStrategy);
    }

    /**
     * @dev Toggle auto-execution for a triple
     */
    function toggleAutoExecution(bytes32 tripleId, bool enabled) 
        external 
        onlyOwner 
    {
        strategies[tripleId].autoExecute = enabled;
        emit AutoExecutionToggled(tripleId, enabled);
    }

    /**
     * @dev Enhanced execution check using AEON math for spread and gas efficiency
     * @param tripleId Token triple identifier
     * @param amount Trade amount
     * @param strategy Execution strategy
     * @return shouldExecute True if arbitrage should be executed
     */
    function _shouldExecuteWithAEONMath(
        bytes32 tripleId,
        uint256 amount,
        ExecutionStrategy memory strategy
    ) internal view returns (bool shouldExecute) {
        TokenTriple memory triple = tokenTriples[tripleId];

        // Get mock prices for spread calculation (in production, use real DEX prices)
        uint256 impliedPrice = 1.001e18; // Mock 0.1% spread
        uint256 externalPrice = 1e18;

        // Calculate spread in basis points
        int256 spreadBps;
        if (impliedPrice > externalPrice) {
            uint256 diff = impliedPrice - externalPrice;
            spreadBps = int256((diff * 10000) / externalPrice);
        } else {
            uint256 diff = externalPrice - impliedPrice;
            spreadBps = -int256((diff * 10000) / externalPrice);
        }

        // Check if spread exceeds minimum threshold (23bps + fees)
        uint256 totalFeesBps = 23; // 23bps minimum threshold
        uint256 absSpread = uint256(spreadBps > 0 ? spreadBps : -spreadBps);
        if (absSpread < totalFeesBps) {
            return false;
        }

        // Calculate gas efficiency score
        uint256 expectedProfitUSD = amount * 1; // Mock: assume $1 per token
        uint256 gasUsed = 200000; // Estimated gas usage
        uint256 gasPriceWei = tx.gasprice;

        uint256 gasCostWei = gasUsed * gasPriceWei;
        uint256 gasCostUSD = (gasCostWei / 1e18) * 2000; // Assume $2000 ETH

        // Require positive efficiency (profit > gas cost)
        if (expectedProfitUSD <= gasCostUSD) {
            return false;
        }

        // Calculate slippage based on spread (simplified)
        uint256 slippageBps = absSpread;

        // Check slippage is acceptable
        if (slippageBps > strategy.maxSlippageBps) {
            return false;
        }

        return true;
    }

    /**
     * @dev Emergency pause
     */
    function pause() external onlyOwner {
        _pause();
    }

    /**
     * @dev Unpause
     */
    function unpause() external onlyOwner {
        _unpause();
    }

    /**
     * @dev Get execution history for a triple
     */
    function getExecutionHistory(bytes32 tripleId, uint256 limit) 
        external 
        view 
        returns (ArbitrageExecution[] memory executions) 
    {
        ArbitrageExecution[] storage history = executionHistory[tripleId];
        uint256 length = history.length > limit ? limit : history.length;
        
        executions = new ArbitrageExecution[](length);
        for (uint256 i = 0; i < length; i++) {
            executions[i] = history[history.length - 1 - i]; // Most recent first
        }
    }
}

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "./libraries/SpreadCalculator.sol";
import "./libraries/BalancerMath.sol";

/**
 * @title PriceMonitor
 * @dev Real-time price monitoring with Chainlink feeds and external API integration
 * Calculates spreadBps and detects arbitrage opportunities with 23bps threshold
 */
contract PriceMonitor is Ownable, ReentrancyGuard {
    using SpreadCalculator for uint256;

    // Chainlink price feeds (Base Sepolia)
    mapping(address => AggregatorV3Interface) public priceFeeds;
    
    // External price sources
    mapping(address => uint256) public externalPrices;
    mapping(address => uint256) public lastPriceUpdate;
    
    // DEX implied prices
    mapping(bytes32 => uint256) public impliedPrices; // keccak256(tokenA, tokenB, dex)
    
    struct PriceData {
        uint256 chainlinkPrice;
        uint256 externalPrice;
        uint256 impliedPrice;
        int256 spreadBps;
        uint256 timestamp;
        bool isStale;
        uint256 confidence;
    }

    struct ArbitrageAlert {
        address tokenA;
        address tokenB;
        address dexAddress;
        int256 spreadBps;
        uint256 estimatedProfit;
        uint256 timestamp;
        bool isActive;
        string dexType; // "balancer", "curve", "uniswap"
    }

    // Events
    event PriceUpdated(
        address indexed token,
        uint256 chainlinkPrice,
        uint256 externalPrice,
        uint256 impliedPrice,
        int256 spreadBps
    );

    event ArbitrageOpportunity(
        address indexed tokenA,
        address indexed tokenB,
        address indexed dex,
        int256 spreadBps,
        uint256 estimatedProfit,
        string dexType
    );

    event SpreadThresholdBreached(
        address indexed tokenA,
        address indexed tokenB,
        int256 spreadBps,
        uint256 threshold
    );

    // Configuration
    uint256 public constant PRICE_STALENESS_THRESHOLD = 3600; // 1 hour
    uint256 public constant MIN_CONFIDENCE_LEVEL = 80; // 80%
    uint256 public spreadAlertThreshold = 23; // 23 bps
    
    // State
    mapping(bytes32 => ArbitrageAlert) public activeAlerts;
    bytes32[] public alertIds;
    uint256 public totalAlertsGenerated;

    constructor() {
        _initializePriceFeeds();
    }

    /**
     * @dev Initialize Chainlink price feeds for Base Sepolia
     */
    function _initializePriceFeeds() internal {
        // Base Sepolia Chainlink feeds
        priceFeeds[0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb] = AggregatorV3Interface(0x591e79239a7d679378eC8c847e5038150364C78F); // DAI/USD
        priceFeeds[0x036CbD53842c5426634e7929541eC2318f3dCF7e] = AggregatorV3Interface(0xd30e2101a97dcbAeBCBC04F14C3f624E67A35165); // USDC/USD
        priceFeeds[0x4200000000000000000000000000000000000006] = AggregatorV3Interface(0xD276fCF34D54A9267738e680A72b7EaF2E54f2E4); // ETH/USD
    }

    /**
     * @dev Get latest price from Chainlink feed
     * @param token Token address
     * @return price Latest price in 18 decimals
     * @return isStale True if price is stale
     */
    function getChainlinkPrice(address token) 
        public 
        view 
        returns (uint256 price, bool isStale) 
    {
        AggregatorV3Interface priceFeed = priceFeeds[token];
        require(address(priceFeed) != address(0), "PriceMonitor: FEED_NOT_FOUND");

        try priceFeed.latestRoundData() returns (
            uint80 roundId,
            int256 answer,
            uint256 startedAt,
            uint256 updatedAt,
            uint80 answeredInRound
        ) {
            require(answer > 0, "PriceMonitor: INVALID_PRICE");
            
            // Convert to 18 decimals (Chainlink feeds are typically 8 decimals)
            uint8 decimals = priceFeed.decimals();
            price = uint256(answer) * (10 ** (18 - decimals));
            
            // Check if price is stale
            isStale = (block.timestamp - updatedAt) > PRICE_STALENESS_THRESHOLD;
            
        } catch {
            revert("PriceMonitor: CHAINLINK_ERROR");
        }
    }

    /**
     * @dev Update external price (from 0x API, 1inch, etc.)
     * @param token Token address
     * @param price Price in 18 decimals
     * @param source Price source identifier
     */
    function updateExternalPrice(
        address token,
        uint256 price,
        string calldata source
    ) external onlyOwner {
        require(price > 0, "PriceMonitor: ZERO_PRICE");
        
        externalPrices[token] = price;
        lastPriceUpdate[token] = block.timestamp;
        
        emit PriceUpdated(token, 0, price, 0, 0);
    }

    /**
     * @dev Update implied price from DEX
     * @param tokenA Token A address
     * @param tokenB Token B address
     * @param dexAddress DEX contract address
     * @param price Implied price from DEX
     * @param dexType DEX type ("balancer", "curve", "uniswap")
     */
    function updateImpliedPrice(
        address tokenA,
        address tokenB,
        address dexAddress,
        uint256 price,
        string calldata dexType
    ) external {
        require(price > 0, "PriceMonitor: ZERO_PRICE");
        
        bytes32 key = keccak256(abi.encodePacked(tokenA, tokenB, dexAddress));
        impliedPrices[key] = price;
        
        // Check for arbitrage opportunity
        _checkArbitrageOpportunity(tokenA, tokenB, dexAddress, price, dexType);
    }

    /**
     * @dev Calculate spread between implied and external price
     * @param tokenA Token A address
     * @param tokenB Token B address
     * @param dexAddress DEX address
     * @return spreadBps Spread in basis points
     * @return impliedPrice DEX implied price
     * @return externalPrice External reference price
     */
    function calculateSpread(
        address tokenA,
        address tokenB,
        address dexAddress
    ) external view returns (
        int256 spreadBps,
        uint256 impliedPrice,
        uint256 externalPrice
    ) {
        bytes32 key = keccak256(abi.encodePacked(tokenA, tokenB, dexAddress));
        impliedPrice = impliedPrices[key];
        
        // Get external price (prefer Chainlink, fallback to external APIs)
        (uint256 chainlinkPrice, bool isStale) = getChainlinkPrice(tokenA);
        if (!isStale && chainlinkPrice > 0) {
            externalPrice = chainlinkPrice;
        } else {
            externalPrice = externalPrices[tokenA];
        }
        
        require(impliedPrice > 0 && externalPrice > 0, "PriceMonitor: INVALID_PRICES");
        
        spreadBps = SpreadCalculator.calculateSpreadBps(impliedPrice, externalPrice);
    }

    /**
     * @dev Get comprehensive price data for a token pair
     * @param tokenA Token A address
     * @param tokenB Token B address
     * @param dexAddress DEX address
     * @return priceData Complete price analysis
     */
    function getPriceData(
        address tokenA,
        address tokenB,
        address dexAddress
    ) external view returns (PriceData memory priceData) {
        (uint256 chainlinkPrice, bool isStale) = getChainlinkPrice(tokenA);
        
        bytes32 key = keccak256(abi.encodePacked(tokenA, tokenB, dexAddress));
        uint256 impliedPrice = impliedPrices[key];
        uint256 externalPrice = externalPrices[tokenA];
        
        // Use best available external price
        uint256 referencePrice = (!isStale && chainlinkPrice > 0) ? chainlinkPrice : externalPrice;
        
        int256 spreadBps = 0;
        if (impliedPrice > 0 && referencePrice > 0) {
            spreadBps = SpreadCalculator.calculateSpreadBps(impliedPrice, referencePrice);
        }
        
        priceData = PriceData({
            chainlinkPrice: chainlinkPrice,
            externalPrice: externalPrice,
            impliedPrice: impliedPrice,
            spreadBps: spreadBps,
            timestamp: block.timestamp,
            isStale: isStale,
            confidence: _calculateConfidence(chainlinkPrice, externalPrice, isStale)
        });
    }

    /**
     * @dev Monitor multiple token pairs for arbitrage opportunities
     * @param tokenPairs Array of token pair addresses
     * @param dexAddresses Array of DEX addresses
     * @param amounts Array of trade amounts
     * @return opportunities Array of detected opportunities
     */
    function monitorArbitrageOpportunities(
        address[][] calldata tokenPairs,
        address[] calldata dexAddresses,
        uint256[] calldata amounts
    ) external view returns (ArbitrageAlert[] memory opportunities) {
        require(
            tokenPairs.length == dexAddresses.length && 
            dexAddresses.length == amounts.length,
            "PriceMonitor: ARRAY_LENGTH_MISMATCH"
        );
        
        opportunities = new ArbitrageAlert[](tokenPairs.length);
        
        for (uint256 i = 0; i < tokenPairs.length; i++) {
            require(tokenPairs[i].length == 2, "PriceMonitor: INVALID_PAIR");
            
            (int256 spreadBps, uint256 impliedPrice, uint256 externalPrice) = 
                this.calculateSpread(tokenPairs[i][0], tokenPairs[i][1], dexAddresses[i]);
            
            if (SpreadCalculator.isProfitableSpread(spreadBps)) {
                (uint256 netProfit, ) = SpreadCalculator.calculateProfit(
                    amounts[i],
                    spreadBps,
                    0 // Gas estimate would be calculated separately
                );
                
                opportunities[i] = ArbitrageAlert({
                    tokenA: tokenPairs[i][0],
                    tokenB: tokenPairs[i][1],
                    dexAddress: dexAddresses[i],
                    spreadBps: spreadBps,
                    estimatedProfit: netProfit,
                    timestamp: block.timestamp,
                    isActive: true,
                    dexType: "unknown" // Would be determined by DEX address
                });
            }
        }
    }

    /**
     * @dev Check for arbitrage opportunity and create alert if threshold met
     */
    function _checkArbitrageOpportunity(
        address tokenA,
        address tokenB,
        address dexAddress,
        uint256 impliedPrice,
        string memory dexType
    ) internal {
        // Get external reference price
        (uint256 chainlinkPrice, bool isStale) = getChainlinkPrice(tokenA);
        uint256 externalPrice = (!isStale && chainlinkPrice > 0) ? 
            chainlinkPrice : externalPrices[tokenA];
        
        if (externalPrice == 0) return; // No reference price available
        
        int256 spreadBps = SpreadCalculator.calculateSpreadBps(impliedPrice, externalPrice);
        
        emit PriceUpdated(tokenA, chainlinkPrice, externalPrice, impliedPrice, spreadBps);
        
        // Check if spread exceeds threshold
        uint256 absoluteSpread = spreadBps >= 0 ? uint256(spreadBps) : uint256(-spreadBps);
        
        if (absoluteSpread >= spreadAlertThreshold) {
            bytes32 alertId = keccak256(abi.encodePacked(
                tokenA, tokenB, dexAddress, block.timestamp
            ));
            
            // Estimate profit for 1 ETH trade
            uint256 tradeAmount = 1 ether;
            (uint256 estimatedProfit, ) = SpreadCalculator.calculateProfit(
                tradeAmount,
                spreadBps,
                0 // Gas cost would be estimated separately
            );
            
            activeAlerts[alertId] = ArbitrageAlert({
                tokenA: tokenA,
                tokenB: tokenB,
                dexAddress: dexAddress,
                spreadBps: spreadBps,
                estimatedProfit: estimatedProfit,
                timestamp: block.timestamp,
                isActive: true,
                dexType: dexType
            });
            
            alertIds.push(alertId);
            totalAlertsGenerated++;
            
            emit ArbitrageOpportunity(
                tokenA,
                tokenB,
                dexAddress,
                spreadBps,
                estimatedProfit,
                dexType
            );
            
            emit SpreadThresholdBreached(tokenA, tokenB, spreadBps, spreadAlertThreshold);
        }
    }

    /**
     * @dev Calculate confidence level for price data
     */
    function _calculateConfidence(
        uint256 chainlinkPrice,
        uint256 externalPrice,
        bool isStale
    ) internal pure returns (uint256 confidence) {
        if (isStale) return 30; // Low confidence for stale data
        
        if (chainlinkPrice > 0 && externalPrice > 0) {
            // Compare Chainlink and external prices
            uint256 priceDiff = chainlinkPrice > externalPrice ? 
                chainlinkPrice - externalPrice : externalPrice - chainlinkPrice;
            uint256 diffPercent = priceDiff * 100 / chainlinkPrice;
            
            if (diffPercent <= 1) return 95; // Very high confidence
            if (diffPercent <= 3) return 85; // High confidence
            if (diffPercent <= 5) return 70; // Medium confidence
            return 50; // Low confidence
        }
        
        return chainlinkPrice > 0 ? 80 : 60; // Chainlink only vs external only
    }

    /**
     * @dev Get active arbitrage alerts
     * @param limit Maximum number of alerts to return
     * @return alerts Array of active alerts
     */
    function getActiveAlerts(uint256 limit) 
        external 
        view 
        returns (ArbitrageAlert[] memory alerts) 
    {
        uint256 count = alertIds.length > limit ? limit : alertIds.length;
        alerts = new ArbitrageAlert[](count);
        
        uint256 activeCount = 0;
        for (uint256 i = alertIds.length; i > 0 && activeCount < count; i--) {
            bytes32 alertId = alertIds[i - 1];
            if (activeAlerts[alertId].isActive) {
                alerts[activeCount] = activeAlerts[alertId];
                activeCount++;
            }
        }
        
        // Resize array to actual count
        assembly {
            mstore(alerts, activeCount)
        }
    }

    /**
     * @dev Deactivate alert (called after arbitrage execution)
     * @param alertId Alert identifier
     */
    function deactivateAlert(bytes32 alertId) external onlyOwner {
        activeAlerts[alertId].isActive = false;
    }

    /**
     * @dev Update spread alert threshold
     * @param newThreshold New threshold in basis points
     */
    function updateSpreadThreshold(uint256 newThreshold) external onlyOwner {
        require(newThreshold >= SpreadCalculator.MIN_SPREAD_BPS, "PriceMonitor: THRESHOLD_TOO_LOW");
        spreadAlertThreshold = newThreshold;
    }

    /**
     * @dev Add new price feed
     * @param token Token address
     * @param feedAddress Chainlink feed address
     */
    function addPriceFeed(address token, address feedAddress) external onlyOwner {
        require(token != address(0) && feedAddress != address(0), "PriceMonitor: ZERO_ADDRESS");
        priceFeeds[token] = AggregatorV3Interface(feedAddress);
    }
}

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@aave/core-v3/contracts/flashloan/base/FlashLoanSimpleReceiverBase.sol";
import "@aave/core-v3/contracts/interfaces/IPoolAddressesProvider.sol";
import "@aave/core-v3/contracts/interfaces/IPool.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title FlashLoanArbitrage
 * @dev Advanced arbitrage contract with AAVE V3 flash loan integration
 * Supports multi-DEX arbitrage with flash loans for maximum capital efficiency
 */
contract FlashLoanArbitrage is FlashLoanSimpleReceiverBase, Ownable, ReentrancyGuard {
    
    // Events
    event ArbitrageExecuted(
        address indexed token,
        uint256 amountIn,
        uint256 profit,
        uint256 gasUsed
    );
    
    event FlashLoanArbitrageExecuted(
        address indexed asset,
        uint256 amount,
        uint256 profit,
        uint256 flashLoanFee
    );
    
    event ArbitrageFailed(
        address indexed token,
        uint256 amountIn,
        string reason
    );

    // State variables
    mapping(address => bool) public authorizedCallers;
    uint256 public totalProfit;
    uint256 public totalTrades;
    uint256 public successfulTrades;
    bool public paused;

    // DEX Router interfaces (simplified)
    struct DEXInfo {
        address router;
        bool enabled;
    }
    
    mapping(string => DEXInfo) public dexRouters;

    modifier onlyAuthorized() {
        require(authorizedCallers[msg.sender] || msg.sender == owner(), "Not authorized");
        _;
    }

    modifier whenNotPaused() {
        require(!paused, "Contract is paused");
        _;
    }

    constructor(address _addressProvider)
        FlashLoanSimpleReceiverBase(IPoolAddressesProvider(_addressProvider))
        Ownable(msg.sender)
    {
        // Initialize DEX routers (Base Sepolia addresses)
        dexRouters["uniswap"] = DEXInfo({
            router: 0x94cC0AaC535CCDB3C01d6787D6413C739ae12bc4, // Uniswap V3 SwapRouter
            enabled: true
        });
        
        dexRouters["sushiswap"] = DEXInfo({
            router: 0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506, // SushiSwap Router
            enabled: true
        });

        authorizedCallers[msg.sender] = true;
    }

    /**
     * @dev Execute flash loan arbitrage
     * @param asset The asset to flash loan
     * @param amount The amount to flash loan
     * @param params Encoded arbitrage parameters
     */
    function executeFlashLoanArbitrage(
        address asset,
        uint256 amount,
        bytes calldata params
    ) external onlyAuthorized whenNotPaused nonReentrant {
        
        // Initiate flash loan
        POOL.flashLoanSimple(
            address(this),
            asset,
            amount,
            params,
            0 // referral code
        );
    }

    /**
     * @dev AAVE flash loan callback - executes the arbitrage logic
     * @param asset The asset that was flash loaned
     * @param amount The amount that was flash loaned
     * @param premium The flash loan fee
     * @param initiator The initiator of the flash loan
     * @param params The encoded arbitrage parameters
     */
    function executeOperation(
        address asset,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata params
    ) external override returns (bool) {
        
        require(msg.sender == address(POOL), "Caller must be AAVE Pool");
        require(initiator == address(this), "Initiator must be this contract");

        // Decode arbitrage parameters
        (
            address tokenA,
            address tokenB,
            string memory buyDex,
            string memory sellDex,
            uint256 minProfit,
            // uint256 flashLoanAmount - unused in this implementation
        ) = abi.decode(params, (address, address, string, string, uint256, uint256));

        uint256 startBalance = IERC20(asset).balanceOf(address(this));
        
        try this.performArbitrage(
            tokenA,
            tokenB,
            amount,
            buyDex,
            sellDex,
            minProfit
        ) {
            uint256 endBalance = IERC20(asset).balanceOf(address(this));
            uint256 profit = endBalance > startBalance ? endBalance - startBalance : 0;
            
            // Ensure we can repay the flash loan
            uint256 amountOwed = amount + premium;
            require(endBalance >= amountOwed, "Insufficient funds to repay flash loan");
            
            // Calculate net profit after flash loan fee
            uint256 netProfit = profit > premium ? profit - premium : 0;
            
            totalProfit += netProfit;
            totalTrades++;
            successfulTrades++;
            
            emit FlashLoanArbitrageExecuted(asset, amount, netProfit, premium);
            
        } catch Error(string memory reason) {
            emit ArbitrageFailed(asset, amount, reason);
            totalTrades++;
        }

        // Approve the Pool contract to pull the owed amount
        IERC20(asset).approve(address(POOL), amount + premium);
        
        return true;
    }

    /**
     * @dev Perform the actual arbitrage between DEXes
     * @param tokenA Input token address
     * @param tokenB Output token address  
     * @param amount Amount to trade
     * @param buyDex DEX to buy from
     * @param sellDex DEX to sell to
     * @param minProfit Minimum profit required
     */
    function performArbitrage(
        address tokenA,
        address tokenB,
        uint256 amount,
        string memory buyDex,
        string memory sellDex,
        uint256 minProfit
    ) external {
        require(msg.sender == address(this), "Internal function only");
        
        // Step 1: Buy tokenB with tokenA on buyDex
        uint256 tokenBAmount = _swapOnDEX(tokenA, tokenB, amount, buyDex);
        require(tokenBAmount > 0, "Buy swap failed");
        
        // Step 2: Sell tokenB for tokenA on sellDex
        uint256 tokenAReceived = _swapOnDEX(tokenB, tokenA, tokenBAmount, sellDex);
        require(tokenAReceived > 0, "Sell swap failed");
        
        // Step 3: Verify profit
        require(tokenAReceived > amount, "No arbitrage profit");
        uint256 profit = tokenAReceived - amount;
        require(profit >= minProfit, "Profit below minimum threshold");
        
        emit ArbitrageExecuted(tokenA, amount, profit, gasleft());
    }

    /**
     * @dev Execute swap on specified DEX
     * @param tokenIn Input token
     * @param amountIn Input amount
     * @param dexName DEX identifier
     * @return amountOut Output amount received
     */
    function _swapOnDEX(
        address tokenIn,
        address /* tokenOut */,
        uint256 amountIn,
        string memory dexName
    ) internal returns (uint256 amountOut) {
        
        DEXInfo memory dex = dexRouters[dexName];
        require(dex.enabled && dex.router != address(0), "DEX not supported");
        
        // Approve token spending
        IERC20(tokenIn).approve(dex.router, amountIn);
        
        // This is a simplified swap - in production you'd implement
        // specific swap logic for each DEX (Uniswap V3, SushiSwap, etc.)
        
        // For now, return a mock amount (replace with actual DEX integration)
        // In production, this would call the actual DEX router contracts
        amountOut = amountIn * 99 / 100; // Mock 1% slippage
        
        // Mock transfer (replace with actual swap results)
        // The actual implementation would handle the real token swaps
    }

    /**
     * @dev Regular arbitrage without flash loans (for smaller opportunities)
     */
    function executeArbitrage(
        address asset,
        uint256 amount,
        bytes calldata params
    ) external onlyAuthorized whenNotPaused nonReentrant returns (uint256 profit) {
        
        // Decode parameters
        (
            address tokenA,
            address tokenB,
            string memory buyDex,
            string memory sellDex,
            uint256 minProfit
        ) = abi.decode(params, (address, address, string, string, uint256));

        uint256 startBalance = IERC20(asset).balanceOf(address(this));
        
        // Perform arbitrage
        this.performArbitrage(tokenA, tokenB, amount, buyDex, sellDex, minProfit);
        
        uint256 endBalance = IERC20(asset).balanceOf(address(this));
        profit = endBalance > startBalance ? endBalance - startBalance : 0;
        
        totalProfit += profit;
        totalTrades++;
        successfulTrades++;
        
        return profit;
    }

    // Admin functions
    function setAuthorizedCaller(address caller, bool authorized) external onlyOwner {
        authorizedCallers[caller] = authorized;
    }

    function setPaused(bool _paused) external onlyOwner {
        paused = _paused;
    }

    function updateDEXRouter(string memory dexName, address router, bool enabled) external onlyOwner {
        dexRouters[dexName] = DEXInfo({router: router, enabled: enabled});
    }

    // View functions
    function getBalance(address token) external view returns (uint256) {
        return IERC20(token).balanceOf(address(this));
    }

    function getSuccessRate() external view returns (uint256) {
        return totalTrades > 0 ? (successfulTrades * 100) / totalTrades : 0;
    }

    function getTotalProfit() external view returns (uint256) {
        return totalProfit;
    }

    // Emergency functions
    function emergencyWithdraw(address token, uint256 amount) external onlyOwner {
        IERC20(token).transfer(owner(), amount);
    }

    receive() external payable {}
}

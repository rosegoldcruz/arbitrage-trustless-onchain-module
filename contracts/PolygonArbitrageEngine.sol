// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

interface IPoolAddressesProvider {
    function getPool() external view returns (address);
}

interface IPool {
    function flashLoan(
        address receiverAddress,
        address[] calldata assets,
        uint256[] calldata amounts,
        uint256[] calldata modes,
        address onBehalfOf,
        bytes calldata params,
        uint16 referralCode
    ) external;
}

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
    function approve(address spender, uint256 amount) external returns (bool);
    function decimals() external view returns (uint8);
}

// Uniswap V3 Interfaces
interface ISwapRouter {
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
    
    function exactInputSingle(ExactInputSingleParams calldata params) external payable returns (uint256 amountOut);
}

interface IQuoter {
    function quoteExactInputSingle(
        address tokenIn,
        address tokenOut,
        uint24 fee,
        uint256 amountIn,
        uint160 sqrtPriceLimitX96
    ) external returns (uint256 amountOut);
}

// QuickSwap/SushiSwap Router Interface
interface IUniswapV2Router {
    function getAmountsOut(uint amountIn, address[] calldata path)
        external view returns (uint[] memory amounts);
    
    function swapExactTokensForTokens(
        uint amountIn,
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external returns (uint[] memory amounts);
}

// Balancer V2 Interfaces
interface IVault {
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
 * @title PolygonArbitrageEngine
 * @dev Complete MEV arbitrage engine for Polygon with multi-DEX integration
 */
contract PolygonArbitrageEngine {
    
    // Aave V3 Polygon addresses
    IPoolAddressesProvider public constant ADDRESSES_PROVIDER = 
        IPoolAddressesProvider(0xa97684ead0e402dC232d5A977953DF7ECBaB3CDb);
    
    // Polygon DEX addresses
    ISwapRouter public constant UNISWAP_V3_ROUTER = ISwapRouter(0xE592427A0AEce92De3Edee1F18E0157C05861564);
    IQuoter public constant UNISWAP_V3_QUOTER = IQuoter(0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6);
    IUniswapV2Router public constant QUICKSWAP_ROUTER = IUniswapV2Router(0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff);
    IUniswapV2Router public constant SUSHISWAP_ROUTER = IUniswapV2Router(0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506);
    IVault public constant BALANCER_VAULT = IVault(0xBA12222222228d8Ba445958a75a0704d566BF2C8);
    
    // Common token addresses on Polygon
    address public constant WETH = 0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619;
    address public constant USDC = 0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174;
    address public constant USDT = 0xc2132D05D31c914a87C6611C10748AEb04B58e8F;
    address public constant DAI = 0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063;
    address public constant WMATIC = 0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270;
    
    // Trading parameters
    uint256 public constant MAX_SLIPPAGE_BPS = 300; // 3%
    uint256 public constant MIN_PROFIT_BPS = 23; // 0.23%
    uint256 public constant MAX_GAS_PRICE = 100 gwei;
    
    // DEX identifiers
    enum DEX { UNISWAP_V3, QUICKSWAP, SUSHISWAP, BALANCER }
    
    struct ArbitrageParams {
        address tokenA;
        address tokenB;
        address tokenC;
        DEX dexA;
        DEX dexB;
        DEX dexC;
        uint24 feeA; // For Uniswap V3
        uint24 feeB;
        uint24 feeC;
        bytes32 poolIdA; // For Balancer
        bytes32 poolIdB;
        bytes32 poolIdC;
        uint256 minProfitBps;
    }
    
    address public owner;
    uint256 public totalTrades;
    uint256 public successfulTrades;
    uint256 public totalProfit;
    bool public paused;
    
    mapping(address => bool) public authorizedTraders;
    mapping(address => uint256) public tokenProfits;
    
    event FlashLoanExecuted(address indexed asset, uint256 amount, bool success, uint256 profit);
    event TradeExecuted(address indexed trader, address indexed asset, uint256 amount, bool success);
    event ProfitRecorded(uint256 amount);
    event ArbitrageExecuted(
        address indexed tokenA,
        address indexed tokenB, 
        address indexed tokenC,
        uint256 amountIn,
        uint256 profit,
        DEX dexA,
        DEX dexB,
        DEX dexC
    );
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }
    
    modifier whenNotPaused() {
        require(!paused, "Contract paused");
        _;
    }
    
    modifier onlyAuthorized() {
        require(authorizedTraders[msg.sender] || msg.sender == owner, "Not authorized");
        _;
    }
    
    constructor() {
        owner = msg.sender;
        authorizedTraders[msg.sender] = true;
        paused = false;
    }
    
    /**
     * @dev Execute flash loan arbitrage with multi-DEX support
     * @param asset The asset to flash loan
     * @param amount The amount to flash loan
     * @param params Encoded arbitrage parameters
     */
    function executeFlashLoanArbitrage(
        address asset,
        uint256 amount,
        bytes calldata params
    ) external whenNotPaused onlyAuthorized {
        
        totalTrades++;
        
        // Prepare flash loan parameters
        address[] memory assets = new address[](1);
        uint256[] memory amounts = new uint256[](1);
        uint256[] memory modes = new uint256[](1);
        
        assets[0] = asset;
        amounts[0] = amount;
        modes[0] = 0; // No debt, pay back immediately
        
        // Get Aave Pool
        IPool pool = IPool(ADDRESSES_PROVIDER.getPool());
        
        // Execute flash loan
        pool.flashLoan(
            address(this),
            assets,
            amounts,
            modes,
            address(this),
            params,
            0 // referral code
        );
        
        emit TradeExecuted(msg.sender, asset, amount, true);
    }
    
    /**
     * @dev Aave flash loan callback - executes the arbitrage
     */
    function executeOperation(
        address[] calldata assets,
        uint256[] calldata amounts,
        uint256[] calldata premiums,
        address initiator,
        bytes calldata params
    ) external returns (bool) {
        
        // Verify this is called by Aave Pool
        require(msg.sender == ADDRESSES_PROVIDER.getPool(), "Invalid caller");
        require(initiator == address(this), "Invalid initiator");
        
        // Execute arbitrage logic
        bool arbitrageSuccess = _executeArbitrage(assets[0], amounts[0], params);
        
        // Calculate total amount to repay (loan + premium)
        uint256 totalRepayment = amounts[0] + premiums[0];
        
        // Ensure we have enough balance to repay
        IERC20 token = IERC20(assets[0]);
        require(token.balanceOf(address(this)) >= totalRepayment, "Insufficient balance for repayment");
        
        // Approve Aave Pool to pull the repayment
        token.approve(msg.sender, totalRepayment);
        
        // Record success/failure and profit
        if (arbitrageSuccess) {
            successfulTrades++;
            uint256 currentBalance = token.balanceOf(address(this));
            if (currentBalance > totalRepayment) {
                uint256 profit = currentBalance - totalRepayment;
                totalProfit += profit;
                tokenProfits[assets[0]] += profit;
                emit ProfitRecorded(profit);
            }
        }
        
        emit FlashLoanExecuted(assets[0], amounts[0], arbitrageSuccess, 0);
        
        return true;
    }

    /**
     * @dev Execute triangular arbitrage across multiple DEXs
     * @param asset The flash loaned asset
     * @param amount The flash loan amount
     * @param params Encoded arbitrage parameters
     */
    function _executeArbitrage(
        address asset,
        uint256 amount,
        bytes calldata params
    ) internal returns (bool) {

        // Decode arbitrage parameters
        ArbitrageParams memory arbParams = abi.decode(params, (ArbitrageParams));

        // Validate that we start and end with the same token
        require(arbParams.tokenA == asset, "Token A must match flash loan asset");

        // Calculate minimum amount out accounting for flash loan fee (0.09%)
        uint256 flashLoanFee = (amount * 9) / 10000; // 0.09%
        uint256 minAmountOut = amount + flashLoanFee;

        // Estimate gas cost in token terms (approximate)
        uint256 estimatedGasCost = _estimateGasCostInToken(asset);
        minAmountOut += estimatedGasCost;

        uint256 currentAmount = amount;
        address currentToken = asset;

        // Step 1: Token A → Token B
        uint256 amountOut1 = _performSwap(
            currentToken,
            arbParams.tokenB,
            currentAmount,
            arbParams.dexA,
            arbParams.feeA,
            arbParams.poolIdA
        );

        if (amountOut1 == 0) return false;

        currentAmount = amountOut1;
        currentToken = arbParams.tokenB;

        // Step 2: Token B → Token C
        uint256 amountOut2 = _performSwap(
            currentToken,
            arbParams.tokenC,
            currentAmount,
            arbParams.dexB,
            arbParams.feeB,
            arbParams.poolIdB
        );

        if (amountOut2 == 0) return false;

        currentAmount = amountOut2;
        currentToken = arbParams.tokenC;

        // Step 3: Token C → Token A
        uint256 finalAmount = _performSwap(
            currentToken,
            arbParams.tokenA,
            currentAmount,
            arbParams.dexC,
            arbParams.feeC,
            arbParams.poolIdC
        );

        if (finalAmount == 0) return false;

        // Validate profitability
        if (finalAmount > minAmountOut) {
            uint256 profit = finalAmount - amount;
            uint256 profitBps = (profit * 10000) / amount;

            // Ensure minimum profit threshold is met
            if (profitBps >= arbParams.minProfitBps) {
                emit ArbitrageExecuted(
                    arbParams.tokenA,
                    arbParams.tokenB,
                    arbParams.tokenC,
                    amount,
                    profit,
                    arbParams.dexA,
                    arbParams.dexB,
                    arbParams.dexC
                );
                return true;
            }
        }

        return false;
    }

    /**
     * @dev Perform swap on specified DEX
     * @param tokenIn Input token
     * @param tokenOut Output token
     * @param amountIn Input amount
     * @param dex DEX to use for swap
     * @param fee Fee tier (for Uniswap V3)
     * @param poolId Pool ID (for Balancer)
     */
    function _performSwap(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        DEX dex,
        uint24 fee,
        bytes32 poolId
    ) internal returns (uint256 amountOut) {

        if (dex == DEX.UNISWAP_V3) {
            return _swapUniswapV3(tokenIn, tokenOut, amountIn, fee);
        } else if (dex == DEX.QUICKSWAP) {
            return _swapQuickSwap(tokenIn, tokenOut, amountIn);
        } else if (dex == DEX.SUSHISWAP) {
            return _swapSushiSwap(tokenIn, tokenOut, amountIn);
        } else if (dex == DEX.BALANCER) {
            return _swapBalancer(tokenIn, tokenOut, amountIn, poolId);
        }

        return 0; // Return 0 for unsupported DEX
    }

    /**
     * @dev Estimate gas cost in terms of the given token
     */
    function _estimateGasCostInToken(address token) internal view returns (uint256) {
        // Approximate gas cost: 300,000 gas * 30 gwei = 0.009 MATIC
        // Convert to token terms using rough price ratios
        if (token == WMATIC) {
            return 9 * 10**15; // 0.009 MATIC
        } else if (token == USDC) {
            return 7 * 10**6; // ~$7 in USDC (6 decimals)
        } else if (token == WETH) {
            return 3 * 10**15; // ~0.003 ETH
        }
        return 0; // Default to 0 for unknown tokens
    }

    /**
     * @dev Swap on Uniswap V3
     */
    function _swapUniswapV3(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint24 fee
    ) internal returns (uint256 amountOut) {

        IERC20(tokenIn).approve(address(UNISWAP_V3_ROUTER), amountIn);

        // Calculate minimum amount out with slippage protection (3% slippage)
        uint256 minAmountOut = (amountIn * 97) / 100; // Simple 3% slippage protection

        ISwapRouter.ExactInputSingleParams memory params = ISwapRouter.ExactInputSingleParams({
            tokenIn: tokenIn,
            tokenOut: tokenOut,
            fee: fee,
            recipient: address(this),
            deadline: block.timestamp + 300, // 5 minutes
            amountIn: amountIn,
            amountOutMinimum: minAmountOut,
            sqrtPriceLimitX96: 0
        });

        try UNISWAP_V3_ROUTER.exactInputSingle(params) returns (uint256 result) {
            return result;
        } catch {
            return 0;
        }
    }

    /**
     * @dev Swap on QuickSwap
     */
    function _swapQuickSwap(
        address tokenIn,
        address tokenOut,
        uint256 amountIn
    ) internal returns (uint256 amountOut) {

        IERC20(tokenIn).approve(address(QUICKSWAP_ROUTER), amountIn);

        address[] memory path = new address[](2);
        path[0] = tokenIn;
        path[1] = tokenOut;

        // Get expected amount out
        uint256[] memory expectedAmounts = QUICKSWAP_ROUTER.getAmountsOut(amountIn, path);
        uint256 minAmountOut = (expectedAmounts[1] * 97) / 100; // 3% slippage

        try QUICKSWAP_ROUTER.swapExactTokensForTokens(
            amountIn,
            minAmountOut,
            path,
            address(this),
            block.timestamp + 300
        ) returns (uint256[] memory amounts) {
            return amounts[amounts.length - 1];
        } catch {
            return 0;
        }
    }

    /**
     * @dev Swap on SushiSwap
     */
    function _swapSushiSwap(
        address tokenIn,
        address tokenOut,
        uint256 amountIn
    ) internal returns (uint256 amountOut) {

        IERC20(tokenIn).approve(address(SUSHISWAP_ROUTER), amountIn);

        address[] memory path = new address[](2);
        path[0] = tokenIn;
        path[1] = tokenOut;

        // Get expected amount out
        uint256[] memory expectedAmounts = SUSHISWAP_ROUTER.getAmountsOut(amountIn, path);
        uint256 minAmountOut = (expectedAmounts[1] * 97) / 100; // 3% slippage

        try SUSHISWAP_ROUTER.swapExactTokensForTokens(
            amountIn,
            minAmountOut,
            path,
            address(this),
            block.timestamp + 300
        ) returns (uint256[] memory amounts) {
            return amounts[amounts.length - 1];
        } catch {
            return 0;
        }
    }

    /**
     * @dev Swap on Balancer
     */
    function _swapBalancer(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        bytes32 poolId
    ) internal returns (uint256 amountOut) {

        IERC20(tokenIn).approve(address(BALANCER_VAULT), amountIn);

        IVault.SingleSwap memory singleSwap = IVault.SingleSwap({
            poolId: poolId,
            kind: 0, // GIVEN_IN
            assetIn: tokenIn,
            assetOut: tokenOut,
            amount: amountIn,
            userData: ""
        });

        IVault.FundManagement memory funds = IVault.FundManagement({
            sender: address(this),
            fromInternalBalance: false,
            recipient: payable(address(this)),
            toInternalBalance: false
        });

        // Calculate minimum amount out (3% slippage)
        uint256 minAmountOut = (amountIn * 97) / 100;

        try BALANCER_VAULT.swap(
            singleSwap,
            funds,
            minAmountOut,
            block.timestamp + 300
        ) returns (uint256 result) {
            return result;
        } catch {
            return 0;
        }
    }

    /**
     * @dev Get quote for Uniswap V3 swap
     */
    function getUniswapV3Quote(
        address tokenIn,
        address tokenOut,
        uint24 fee,
        uint256 amountIn
    ) external returns (uint256 amountOut) {
        return UNISWAP_V3_QUOTER.quoteExactInputSingle(
            tokenIn,
            tokenOut,
            fee,
            amountIn,
            0
        );
    }

    /**
     * @dev Get quote for QuickSwap/SushiSwap
     */
    function getV2Quote(
        address router,
        address tokenIn,
        address tokenOut,
        uint256 amountIn
    ) external view returns (uint256 amountOut) {
        address[] memory path = new address[](2);
        path[0] = tokenIn;
        path[1] = tokenOut;

        uint256[] memory amounts = IUniswapV2Router(router).getAmountsOut(amountIn, path);
        return amounts[amounts.length - 1];
    }

    /**
     * @dev Calculate potential profit for arbitrage opportunity
     */
    function calculateArbitrageProfit(
        ArbitrageParams calldata params,
        uint256 amount
    ) external returns (uint256 estimatedProfit, uint256 profitBps) {

        // Get quotes from each DEX
        uint256 amountAfterSwap1;
        uint256 amountAfterSwap2;
        uint256 finalAmount;

        // First swap quote
        if (params.dexA == DEX.UNISWAP_V3) {
            amountAfterSwap1 = this.getUniswapV3Quote(params.tokenA, params.tokenB, params.feeA, amount);
        } else if (params.dexA == DEX.QUICKSWAP) {
            amountAfterSwap1 = this.getV2Quote(address(QUICKSWAP_ROUTER), params.tokenA, params.tokenB, amount);
        } else if (params.dexA == DEX.SUSHISWAP) {
            amountAfterSwap1 = this.getV2Quote(address(SUSHISWAP_ROUTER), params.tokenA, params.tokenB, amount);
        }

        // Second swap quote
        if (params.dexB == DEX.UNISWAP_V3) {
            amountAfterSwap2 = this.getUniswapV3Quote(params.tokenB, params.tokenC, params.feeB, amountAfterSwap1);
        } else if (params.dexB == DEX.QUICKSWAP) {
            amountAfterSwap2 = this.getV2Quote(address(QUICKSWAP_ROUTER), params.tokenB, params.tokenC, amountAfterSwap1);
        } else if (params.dexB == DEX.SUSHISWAP) {
            amountAfterSwap2 = this.getV2Quote(address(SUSHISWAP_ROUTER), params.tokenB, params.tokenC, amountAfterSwap1);
        }

        // Third swap quote
        if (params.dexC == DEX.UNISWAP_V3) {
            finalAmount = this.getUniswapV3Quote(params.tokenC, params.tokenA, params.feeC, amountAfterSwap2);
        } else if (params.dexC == DEX.QUICKSWAP) {
            finalAmount = this.getV2Quote(address(QUICKSWAP_ROUTER), params.tokenC, params.tokenA, amountAfterSwap2);
        } else if (params.dexC == DEX.SUSHISWAP) {
            finalAmount = this.getV2Quote(address(SUSHISWAP_ROUTER), params.tokenC, params.tokenA, amountAfterSwap2);
        }

        if (finalAmount > amount) {
            estimatedProfit = finalAmount - amount;
            profitBps = (estimatedProfit * 10000) / amount;
        } else {
            estimatedProfit = 0;
            profitBps = 0;
        }
    }

    /**
     * @dev Get contract statistics
     */
    function getStats() external view returns (
        uint256 _totalTrades,
        uint256 _successfulTrades,
        uint256 _totalProfit,
        uint256 _successRate
    ) {
        _totalTrades = totalTrades;
        _successfulTrades = successfulTrades;
        _totalProfit = totalProfit;
        _successRate = totalTrades > 0 ? (successfulTrades * 100) / totalTrades : 0;
    }

    /**
     * @dev Authorize a trader
     */
    function authorizeTrader(address trader) external onlyOwner {
        authorizedTraders[trader] = true;
    }

    /**
     * @dev Revoke trader authorization
     */
    function revokeTrader(address trader) external onlyOwner {
        authorizedTraders[trader] = false;
    }

    /**
     * @dev Pause/unpause contract
     */
    function setPaused(bool _paused) external onlyOwner {
        paused = _paused;
    }

    /**
     * @dev Emergency withdraw tokens
     */
    function emergencyWithdraw(address token) external onlyOwner {
        if (token == address(0)) {
            payable(owner).transfer(address(this).balance);
        } else {
            IERC20(token).transfer(owner, IERC20(token).balanceOf(address(this)));
        }
    }

    /**
     * @dev Receive ETH
     */
    receive() external payable {}
}

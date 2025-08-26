// SPDX-License-Identifier: MIT
pragma solidity ^0.8.22;
/*
  Polygon/Sepolia Aave V3 flashloan arbitrage executor (UUPS upgradeable).
  - CEI, nonReentrant, Pausable, role-gated
  - Router allowlist, per-hop minOut, deadline, minProfit enforced
  - Surplus swept to treasury
  - No unused vars, no TODOs
*/
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/ReentrancyGuardUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/PausableUpgradeable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

import { IPoolAddressesProvider } from "@aave/core-v3/contracts/interfaces/IPoolAddressesProvider.sol";
import { IPool } from "@aave/core-v3/contracts/interfaces/IPool.sol";

contract MEVGuardFlashLoanArbitrage is
    Initializable,
    UUPSUpgradeable,
    OwnableUpgradeable,
    AccessControlUpgradeable,
    ReentrancyGuardUpgradeable,
    PausableUpgradeable
{
    using SafeERC20 for IERC20;

    bytes32 public constant EXECUTOR_ROLE = keccak256("EXECUTOR_ROLE");

    IPool public pool;
    address public treasury;
    uint256 public maxGasPrice;

    mapping(address => bool) public allowedRouter;
    mapping(address => uint256) public minProfitByAsset;
    mapping(address => uint256) public maxFlashLoanAmount;

    bool public onlyTrustedRelayers;
    mapping(address => bool) public trustedRelayer;

    event Initialized(address provider, address treasury, uint256 maxGasPrice);
    event RouterConfigured(string name, address router, uint8 routerType, bool allowed);
    event StrategyUpdated(address indexed asset, uint256 minProfit, uint256 maxFlashAmount);
    event TreasuryUpdated(address indexed treasury);
    event MaxGasUpdated(uint256 maxGasPrice);
    event Pause();
    event Unpause();
    event FlashLoanRequested(address indexed asset, uint256 amount);
    event ArbitrageExecuted(address indexed asset, uint256 amount, uint256 premium, uint256 profit);

    error NotPool();
    error BadInitiator();
    error RouterNotAllowed(address router);
    error DeadlineExpired();
    error GasPriceTooHigh();
    error MinProfitNotMet(uint256 profit, uint256 required);
    error AmountTooLarge(uint256 amount, uint256 maxAllowed);
    error UntrustedRelayer(address sender);

    struct TradeParams {
        address[] routers;
        address[] tokens;         // length = routers.length - 1
        uint256[] minAmountsOut;  // length = routers.length
        bytes[]   routerCalldata; // length = routers.length
        uint256   minProfit;
        uint256   deadline;
    }

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() { _disableInitializers(); }

    function initialize(
        address provider,
        address _treasury,
        uint256 _maxGasPrice
    ) public initializer {
        __Ownable_init(_msgSender());
        __AccessControl_init();
        __ReentrancyGuard_init();
        __Pausable_init();
        __UUPSUpgradeable_init();

        pool = IPool(IPoolAddressesProvider(provider).getPool());
        treasury = _treasury;
        maxGasPrice = _maxGasPrice;

        _grantRole(DEFAULT_ADMIN_ROLE, _msgSender());
        _grantRole(EXECUTOR_ROLE, _msgSender());

        emit Initialized(provider, _treasury, _maxGasPrice);
    }

    function _authorizeUpgrade(address) internal override onlyOwner {}

    // Admin
    function setTreasury(address _treasury) external onlyOwner { treasury = _treasury; emit TreasuryUpdated(_treasury); }
    function setMaxGasPrice(uint256 _wei) external onlyOwner { maxGasPrice = _wei; emit MaxGasUpdated(_wei); }
    function pause() external onlyOwner { _pause(); emit Pause(); }
    function unpause() external onlyOwner { _unpause(); emit Unpause(); }

    function configureRouter(string calldata name, address router, uint8 routerType, bool allowed) external onlyOwner {
        allowedRouter[router] = allowed;
        emit RouterConfigured(name, router, routerType, allowed);
    }

    function updateStrategy(address asset, uint256 minProfit, uint256 maxAmount) external onlyOwner {
        minProfitByAsset[asset] = minProfit;
        maxFlashLoanAmount[asset] = maxAmount;
        emit StrategyUpdated(asset, minProfit, maxAmount);
    }

    function setTrustedRelayers(bool enabled, address[] calldata relayers) external onlyOwner {
        onlyTrustedRelayers = enabled;
        for (uint256 i = 0; i < relayers.length; i++) {
            trustedRelayer[relayers[i]] = true;
        }
    }

    // Entrypoint
    function executeArbitrage(
        address asset,
        uint256 amount,
        bytes calldata encodedParams
    ) external whenNotPaused nonReentrant onlyRole(EXECUTOR_ROLE) {
        if (onlyTrustedRelayers && !trustedRelayer[_msgSender()]) revert UntrustedRelayer(_msgSender());
        if (tx.gasprice > maxGasPrice) revert GasPriceTooHigh();

        uint256 maxAmt = maxFlashLoanAmount[asset];
        if (maxAmt != 0 && amount > maxAmt) revert AmountTooLarge(amount, maxAmt);

        TradeParams memory p = _decodeParams(encodedParams);
        if (block.timestamp > p.deadline) revert DeadlineExpired();

        // Aave V3 requires arrays even for single-asset loans
        address[] memory _assets = new address[](1);
        _assets[0] = asset;

        uint256[] memory _amounts = new uint256[](1);
        _amounts[0] = amount;

        uint256[] memory _modes = new uint256[](1);
        _modes[0] = 0; // no debt, full repayment in callback

        emit FlashLoanRequested(asset, amount);

        pool.flashLoan(
            address(this),
            _assets,
            _amounts,
            _modes,
            address(this),
            encodedParams,
            0 // referralCode
        );
    }

    // Aave callback
    function executeOperation(
        address[] calldata assets,
        uint256[] calldata amounts,
        uint256[] calldata premiums,
        address initiator,
        bytes calldata encodedParams
    ) external nonReentrant returns (bool) {
        if (msg.sender != address(pool)) revert NotPool();
        if (initiator != address(this)) revert BadInitiator();

        TradeParams memory p = _decodeParams(encodedParams);
        if (block.timestamp > p.deadline) revert DeadlineExpired();

        address asset = assets[0];
        uint256 amount = amounts[0];
        uint256 premium = premiums[0];

        uint256 hops = p.routers.length;
        require(p.routerCalldata.length == hops && p.minAmountsOut.length == hops, "Bad params");
        require(p.tokens.length == (hops == 0 ? 0 : hops - 1), "Bad tokens length");

        for (uint256 i = 0; i < hops; i++) {
            address router = p.routers[i];
            if (!allowedRouter[router]) revert RouterNotAllowed(router);

            address tokenIn  = (i == 0) ? asset : p.tokens[i - 1];
            address tokenOut = (i == hops - 1) ? asset : p.tokens[i];

            uint256 balBefore = IERC20(tokenOut).balanceOf(address(this));

            // approve only if needed
            uint256 spend = IERC20(tokenIn).balanceOf(address(this));
            if (spend > 0) {
                uint256 allowance = IERC20(tokenIn).allowance(address(this), router);
                if (allowance < spend) {
                    IERC20(tokenIn).forceApprove(router, spend);
                }
            }

            // slither-disable-next-line reentrancy-benign
            (bool ok, bytes memory ret) = router.call(p.routerCalldata[i]);
            require(ok, _revertMsg(ret));

            uint256 balAfter = IERC20(tokenOut).balanceOf(address(this));
            require(balAfter >= balBefore + p.minAmountsOut[i], "SlippageTooHigh");
        }

        uint256 repay = amount + premium;
        uint256 finalBal = IERC20(asset).balanceOf(address(this));

        // enforce config floor regardless of what caller passed in
        uint256 requiredProfit = p.minProfit;
        uint256 floor = minProfitByAsset[asset];
        if (requiredProfit < floor) requiredProfit = floor;

        if (finalBal < repay + requiredProfit) revert MinProfitNotMet(finalBal - repay, requiredProfit);

        uint256 allowanceRepay = IERC20(asset).allowance(address(this), address(pool));
        if (allowanceRepay < repay) {
            IERC20(asset).forceApprove(address(pool), repay);
        }

        uint256 profit = finalBal - repay;
        if (profit > 0 && treasury != address(0)) IERC20(asset).safeTransfer(treasury, profit);

        emit ArbitrageExecuted(asset, amount, premium, profit);
        return true;
    }

    function sweep(address token, uint256 amount, address to) external onlyOwner {
        IERC20(token).safeTransfer(to, amount);
    }

    function _decodeParams(bytes calldata data) internal pure returns (TradeParams memory p) {
        (address[] memory routers, address[] memory tokens, uint256[] memory minAmountsOut, bytes[] memory routerCalldata, uint256 minProfit, uint256 deadline)
            = abi.decode(data, (address[], address[], uint256[], bytes[], uint256, uint256));
        p.routers = routers; p.tokens = tokens; p.minAmountsOut = minAmountsOut; p.routerCalldata = routerCalldata;
        p.minProfit = minProfit; p.deadline = deadline;
    }

    function _revertMsg(bytes memory ret) internal pure returns (string memory) {
        if (ret.length < 68) return "RouterCallFailed";
        assembly { ret := add(ret, 0x04) }
        return abi.decode(ret, (string));
    }

    uint256[45] private __gap;
}

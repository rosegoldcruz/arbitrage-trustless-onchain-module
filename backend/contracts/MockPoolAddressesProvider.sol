// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title MockPoolAddressesProvider
 * @dev Mock implementation of AAVE's IPoolAddressesProvider for testing
 */
contract MockPoolAddressesProvider {
    address private _pool;
    address private _poolConfigurator;
    address private _priceOracle;
    address private _aclManager;
    address private _aclAdmin;
    address private _priceOracleSentinel;
    address private _dataProvider;
    string private _marketId;

    constructor() {
        _marketId = "Test Market";
        // Deploy a mock pool for testing
        _pool = address(new MockPool());
    }

    function getMarketId() external view returns (string memory) {
        return _marketId;
    }

    function setMarketId(string calldata newMarketId) external {
        _marketId = newMarketId;
    }

    function getAddress(bytes32 id) external view returns (address) {
        if (id == keccak256("POOL")) {
            return _pool;
        } else if (id == keccak256("POOL_CONFIGURATOR")) {
            return _poolConfigurator;
        } else if (id == keccak256("PRICE_ORACLE")) {
            return _priceOracle;
        } else if (id == keccak256("ACL_MANAGER")) {
            return _aclManager;
        } else if (id == keccak256("ACL_ADMIN")) {
            return _aclAdmin;
        } else if (id == keccak256("PRICE_ORACLE_SENTINEL")) {
            return _priceOracleSentinel;
        } else if (id == keccak256("DATA_PROVIDER")) {
            return _dataProvider;
        }
        return address(0);
    }

    function setAddress(bytes32 id, address newAddress) external {
        if (id == keccak256("POOL")) {
            _pool = newAddress;
        } else if (id == keccak256("POOL_CONFIGURATOR")) {
            _poolConfigurator = newAddress;
        } else if (id == keccak256("PRICE_ORACLE")) {
            _priceOracle = newAddress;
        } else if (id == keccak256("ACL_MANAGER")) {
            _aclManager = newAddress;
        } else if (id == keccak256("ACL_ADMIN")) {
            _aclAdmin = newAddress;
        } else if (id == keccak256("PRICE_ORACLE_SENTINEL")) {
            _priceOracleSentinel = newAddress;
        } else if (id == keccak256("DATA_PROVIDER")) {
            _dataProvider = newAddress;
        }
    }

    function getPool() external view returns (address) {
        return _pool;
    }

    function setPoolImpl(address newPoolImpl) external {
        _pool = newPoolImpl;
    }

    function getPoolConfigurator() external view returns (address) {
        return _poolConfigurator;
    }

    function setPoolConfiguratorImpl(address newPoolConfiguratorImpl) external {
        _poolConfigurator = newPoolConfiguratorImpl;
    }

    function getPriceOracle() external view returns (address) {
        return _priceOracle;
    }

    function setPriceOracle(address newPriceOracle) external {
        _priceOracle = newPriceOracle;
    }

    function getACLManager() external view returns (address) {
        return _aclManager;
    }

    function setACLManager(address newAclManager) external {
        _aclManager = newAclManager;
    }

    function getACLAdmin() external view returns (address) {
        return _aclAdmin;
    }

    function setACLAdmin(address newAclAdmin) external {
        _aclAdmin = newAclAdmin;
    }

    function getPriceOracleSentinel() external view returns (address) {
        return _priceOracleSentinel;
    }

    function setPriceOracleSentinel(address newPriceOracleSentinel) external {
        _priceOracleSentinel = newPriceOracleSentinel;
    }

    function getPoolDataProvider() external view returns (address) {
        return _dataProvider;
    }

    function setPoolDataProvider(address newDataProvider) external {
        _dataProvider = newDataProvider;
    }
}

/**
 * @title MockPool
 * @dev Mock implementation of AAVE's IPool for testing flash loans
 */
contract MockPool {
    event FlashLoan(
        address indexed target,
        address indexed initiator,
        address indexed asset,
        uint256 amount,
        uint256 interestRateMode,
        uint256 premium,
        uint16 referralCode
    );

    function flashLoanSimple(
        address receiverAddress,
        address asset,
        uint256 amount,
        bytes calldata params,
        uint16 referralCode
    ) external {
        // Calculate premium (0.09% for AAVE)
        uint256 premium = (amount * 9) / 10000;
        
        // Emit event for testing
        emit FlashLoan(
            receiverAddress,
            msg.sender,
            asset,
            amount,
            0, // Simple flash loan mode
            premium,
            referralCode
        );
        
        // In a real implementation, this would:
        // 1. Transfer tokens to receiver
        // 2. Call executeOperation on receiver
        // 3. Collect repayment + premium
        
        // For testing, we just emit the event
    }

    function supply(
        address asset,
        uint256 amount,
        address onBehalfOf,
        uint16 referralCode
    ) external {
        // Mock supply function
    }

    function withdraw(
        address asset,
        uint256 amount,
        address to
    ) external returns (uint256) {
        // Mock withdraw function
        return amount;
    }

    function borrow(
        address asset,
        uint256 amount,
        uint256 interestRateMode,
        uint16 referralCode,
        address onBehalfOf
    ) external {
        // Mock borrow function
    }

    function repay(
        address asset,
        uint256 amount,
        uint256 interestRateMode,
        address onBehalfOf
    ) external returns (uint256) {
        // Mock repay function
        return amount;
    }
}

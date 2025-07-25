// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title SimpleFlashLoan
 * @dev A simplified flash loan contract for testing and demonstration
 * This contract simulates flash loan functionality without requiring AAVE
 */
contract SimpleFlashLoan is Ownable, ReentrancyGuard {
    
    // Events
    event FlashLoanExecuted(
        address indexed borrower,
        address indexed asset,
        uint256 amount,
        uint256 fee
    );
    
    event FlashLoanRequested(
        address indexed borrower,
        address indexed asset,
        uint256 amount
    );
    
    // State variables
    mapping(address => bool) public authorizedBorrowers;
    mapping(address => uint256) public totalBorrowed;
    uint256 public flashLoanFeePercent = 9; // 0.09% fee (9 basis points)
    uint256 public constant FEE_DENOMINATOR = 10000;
    
    modifier onlyAuthorized() {
        require(authorizedBorrowers[msg.sender] || msg.sender == owner(), "Not authorized");
        _;
    }
    
    constructor() Ownable(msg.sender) {
        authorizedBorrowers[msg.sender] = true;
    }
    
    /**
     * @dev Request a flash loan
     * @param asset The asset to borrow
     * @param amount The amount to borrow
     */
    function requestFlashLoan(
        address asset,
        uint256 amount
    ) external onlyAuthorized nonReentrant {
        
        require(amount > 0, "Amount must be greater than 0");
        
        // Check contract has enough balance
        uint256 contractBalance = IERC20(asset).balanceOf(address(this));
        require(contractBalance >= amount, "Insufficient contract balance");
        
        // Calculate fee
        uint256 fee = (amount * flashLoanFeePercent) / FEE_DENOMINATOR;
        uint256 amountPlusFee = amount + fee;
        
        emit FlashLoanRequested(msg.sender, asset, amount);
        
        // Transfer tokens to borrower
        IERC20(asset).transfer(msg.sender, amount);
        
        // Execute borrower's logic (in a real implementation, this would be a callback)
        // For this demo, we expect the borrower to return the funds + fee manually
        
        // Check repayment (simplified - in production this would be in a callback)
        uint256 balanceAfter = IERC20(asset).balanceOf(address(this));
        require(balanceAfter >= contractBalance + fee, "Flash loan not repaid with fee");
        
        totalBorrowed[asset] += amount;
        
        emit FlashLoanExecuted(msg.sender, asset, amount, fee);
    }
    
    /**
     * @dev Deposit tokens to provide liquidity for flash loans
     * @param asset The asset to deposit
     * @param amount The amount to deposit
     */
    function deposit(address asset, uint256 amount) external {
        require(amount > 0, "Amount must be greater than 0");
        IERC20(asset).transferFrom(msg.sender, address(this), amount);
    }
    
    /**
     * @dev Withdraw tokens (owner only)
     * @param asset The asset to withdraw
     * @param amount The amount to withdraw
     */
    function withdraw(address asset, uint256 amount) external onlyOwner {
        require(amount > 0, "Amount must be greater than 0");
        uint256 balance = IERC20(asset).balanceOf(address(this));
        require(balance >= amount, "Insufficient balance");
        IERC20(asset).transfer(owner(), amount);
    }
    
    /**
     * @dev Set authorized borrower
     * @param borrower The borrower address
     * @param authorized Whether the borrower is authorized
     */
    function setAuthorizedBorrower(address borrower, bool authorized) external onlyOwner {
        authorizedBorrowers[borrower] = authorized;
    }
    
    /**
     * @dev Set flash loan fee percentage
     * @param feePercent The fee percentage in basis points (e.g., 9 = 0.09%)
     */
    function setFlashLoanFee(uint256 feePercent) external onlyOwner {
        require(feePercent <= 1000, "Fee too high"); // Max 10%
        flashLoanFeePercent = feePercent;
    }
    
    /**
     * @dev Get contract balance for an asset
     * @param asset The asset address
     * @return The balance
     */
    function getBalance(address asset) external view returns (uint256) {
        return IERC20(asset).balanceOf(address(this));
    }
    
    /**
     * @dev Calculate flash loan fee
     * @param amount The loan amount
     * @return The fee amount
     */
    function calculateFee(uint256 amount) external view returns (uint256) {
        return (amount * flashLoanFeePercent) / FEE_DENOMINATOR;
    }
    
    /**
     * @dev Emergency function to recover stuck tokens
     * @param asset The asset to recover
     */
    function emergencyRecover(address asset) external onlyOwner {
        uint256 balance = IERC20(asset).balanceOf(address(this));
        if (balance > 0) {
            IERC20(asset).transfer(owner(), balance);
        }
    }
    
    // Allow contract to receive ETH
    receive() external payable {}
}

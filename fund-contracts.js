#!/usr/bin/env node

/**
 * Fund deployed contracts with Base Sepolia ETH
 */

const { ethers } = require("hardhat");
require('dotenv').config();

async function main() {
  console.log("💰 Funding contracts with Base Sepolia ETH...");
  
  const [deployer] = await ethers.getSigners();
  console.log("Funding from account:", deployer.address);
  
  const balance = await ethers.provider.getBalance(deployer.address);
  console.log("Account balance:", ethers.formatEther(balance), "ETH");
  
  // Contract addresses from environment
  const contracts = [
    process.env.FLASHLOAN_EXECUTOR_ADDRESS,
    process.env.AEON_ARBITRAGE_CORE_ADDRESS,
    process.env.PRICE_MONITOR_ADDRESS,
    process.env.TRIANGULAR_ARBITRAGE_ADDRESS
  ].filter(Boolean);
  
  if (contracts.length === 0) {
    console.error("❌ No contract addresses found in environment");
    console.error("💡 Run deploy-contracts.js first");
    process.exit(1);
  }
  
  const fundAmount = ethers.parseEther("0.01"); // 0.01 ETH per contract
  
  console.log(`\n💸 Funding ${contracts.length} contracts with 0.01 ETH each...`);
  
  for (const address of contracts) {
    try {
      const tx = await deployer.sendTransaction({
        to: address,
        value: fundAmount
      });
      
      console.log(`📤 Funding ${address}...`);
      await tx.wait();
      console.log(`✅ Funded ${address} with 0.01 ETH`);
      
    } catch (error) {
      console.error(`❌ Failed to fund ${address}:`, error.message);
    }
  }
  
  console.log("\n✅ Contract funding complete!");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Funding failed:", error);
    process.exit(1);
  });

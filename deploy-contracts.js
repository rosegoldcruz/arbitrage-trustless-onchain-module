#!/usr/bin/env node

/**
 * ATOM Contract Deployment Script for Base Sepolia
 * 
 * This script:
 * 1. Checks for required environment variables
 * 2. Deploys FlashLoanArbitrage and AEON contracts to Base Sepolia
 * 3. Verifies contracts on Basescan
 * 4. Updates environment configuration with deployed addresses
 * 5. Creates a deployment summary
 */

const { ethers } = require("hardhat");
const fs = require('fs');
const path = require('path');
require('dotenv').config();

// Base Sepolia configuration
const BASE_SEPOLIA_CONFIG = {
  chainId: 84532,
  name: "Base Sepolia",
  rpcUrl: "https://sepolia.base.org",
  
  // Aave V3 addresses on Base Sepolia
  aavePoolAddressesProvider: "0x0b8FAe5f9Bf5a1a5867FB5b39fF4C028b1C2ebA9",
  aavePool: "0x07eA79F68B2B3df564D0A34F8e19D9B1e339814b",
  
  // Token addresses (Base Sepolia testnet)
  tokens: {
    DAI: "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb",
    USDC: "0x036CbD53842c5426634e7929541eC2318f3dCF7e", 
    WETH: "0x4200000000000000000000000000000000000006",
    GHO: "0x40D16FC0246aD3160Ccc09B8D0D3A2cD28aE6C2f"
  },
  
  // Chainlink price feeds
  priceFeeds: {
    DAI_USD: "0x591e79239a7d679378eC8c847e5038150364C78F",
    USDC_USD: "0xd30e2101a97dcbAeBCBC04F14C3f624E67A35165",
    ETH_USD: "0xD276fCF34D54A9267738e680A72b7EaF2E54f2E4"
  }
};

function checkEnvironmentVariables() {
  console.log("🔍 Checking environment variables...");
  
  const required = [
    'PRIVATE_KEY',
    'BASE_SEPOLIA_RPC_URL',
    'BASESCAN_API_KEY'
  ];
  
  const missing = required.filter(key => !process.env[key]);
  
  if (missing.length > 0) {
    console.error("❌ Missing required environment variables:");
    missing.forEach(key => console.error(`   - ${key}`));
    console.error("\n📝 Please set these in your .env file:");
    console.error("   PRIVATE_KEY=your_wallet_private_key");
    console.error("   BASE_SEPOLIA_RPC_URL=https://sepolia.base.org");
    console.error("   BASESCAN_API_KEY=your_basescan_api_key");
    console.error("\n💡 Get Base Sepolia ETH from: https://www.coinbase.com/faucets/base-ethereum-sepolia-faucet");
    console.error("💡 Get Basescan API key from: https://basescan.org/apis");
    process.exit(1);
  }
  
  console.log("✅ All required environment variables are set");
}

async function deployContracts() {
  console.log("🚀 Starting ATOM contract deployment to Base Sepolia...");
  console.log("=" .repeat(60));
  
  const [deployer] = await ethers.getSigners();
  console.log("Deploying with account:", deployer.address);
  
  const balance = await ethers.provider.getBalance(deployer.address);
  console.log("Account balance:", ethers.formatEther(balance), "ETH");
  
  if (balance < ethers.parseEther("0.01")) {
    console.error("❌ Insufficient balance! Need at least 0.01 ETH for deployment");
    console.error("💡 Get Base Sepolia ETH from: https://www.coinbase.com/faucets/base-ethereum-sepolia-faucet");
    process.exit(1);
  }
  
  const deployedContracts = {};
  
  try {
    // 1. Deploy FlashLoanArbitrage
    console.log("\n⚡ Deploying FlashLoanArbitrage...");
    const FlashLoanArbitrage = await ethers.getContractFactory("FlashLoanArbitrage");
    const flashLoanArbitrage = await FlashLoanArbitrage.deploy(
      BASE_SEPOLIA_CONFIG.aavePoolAddressesProvider
    );
    await flashLoanArbitrage.waitForDeployment();
    
    deployedContracts.flashLoanArbitrage = await flashLoanArbitrage.getAddress();
    console.log("✅ FlashLoanArbitrage deployed to:", deployedContracts.flashLoanArbitrage);
    
    // 2. Deploy AEON (AEONArbitrageCore)
    console.log("\n🧬 Deploying AEON...");
    const AEON = await ethers.getContractFactory("AEON");
    const aeon = await AEON.deploy(
      BASE_SEPOLIA_CONFIG.aavePoolAddressesProvider
    );
    await aeon.waitForDeployment();
    
    deployedContracts.aeon = await aeon.getAddress();
    console.log("✅ AEON deployed to:", deployedContracts.aeon);
    
    // 3. Deploy PriceMonitor
    console.log("\n📊 Deploying PriceMonitor...");
    const PriceMonitor = await ethers.getContractFactory("PriceMonitor");
    const priceMonitor = await PriceMonitor.deploy();
    await priceMonitor.waitForDeployment();
    
    deployedContracts.priceMonitor = await priceMonitor.getAddress();
    console.log("✅ PriceMonitor deployed to:", deployedContracts.priceMonitor);
    
    // 4. Deploy TriangularArbitrage
    console.log("\n🔺 Deploying TriangularArbitrage...");
    const TriangularArbitrage = await ethers.getContractFactory("TriangularArbitrage");
    const triangularArbitrage = await TriangularArbitrage.deploy(
      BASE_SEPOLIA_CONFIG.aavePoolAddressesProvider
    );
    await triangularArbitrage.waitForDeployment();
    
    deployedContracts.triangularArbitrage = await triangularArbitrage.getAddress();
    console.log("✅ TriangularArbitrage deployed to:", deployedContracts.triangularArbitrage);
    
    // 5. Configure contracts
    console.log("\n🔧 Configuring contracts...");
    
    // Configure AEON
    await aeon.updateConfig(
      23,                                    // minSpreadBps: 23bps
      ethers.parseUnits("50", "gwei"),      // maxGasPrice: 50 gwei
      300,                                   // maxSlippageBps: 3%
      ethers.parseEther("10"),              // minProfitUSD: $10
      ethers.parseEther("10000"),           // maxFlashLoanAmount: $10k
      false,                                // autonomousMode: false (manual for now)
      60                                    // executionCooldown: 60 seconds
    );
    console.log("✅ AEON configured");
    
    // Configure TriangularArbitrage
    await triangularArbitrage.updateConfig(
      ethers.parseUnits("50", "gwei"),      // maxGasPrice: 50 gwei
      300,                                   // maxSlippageBps: 3%
      ethers.parseEther("10")               // minProfitUSD: $10
    );
    console.log("✅ TriangularArbitrage configured");
    
    return deployedContracts;
    
  } catch (error) {
    console.error("\n❌ Deployment failed:", error.message);
    throw error;
  }
}

async function verifyContracts(deployedContracts) {
  if (!process.env.BASESCAN_API_KEY) {
    console.log("\n⚠️  Skipping contract verification (no BASESCAN_API_KEY)");
    return;
  }
  
  console.log("\n🔍 Verifying contracts on Basescan...");
  
  const contracts = [
    {
      name: "FlashLoanArbitrage",
      address: deployedContracts.flashLoanArbitrage,
      constructorArguments: [BASE_SEPOLIA_CONFIG.aavePoolAddressesProvider]
    },
    {
      name: "AEON",
      address: deployedContracts.aeon,
      constructorArguments: [BASE_SEPOLIA_CONFIG.aavePoolAddressesProvider]
    },
    {
      name: "PriceMonitor",
      address: deployedContracts.priceMonitor,
      constructorArguments: []
    },
    {
      name: "TriangularArbitrage",
      address: deployedContracts.triangularArbitrage,
      constructorArguments: [BASE_SEPOLIA_CONFIG.aavePoolAddressesProvider]
    }
  ];
  
  for (const contract of contracts) {
    try {
      console.log(`Verifying ${contract.name}...`);
      await hre.run("verify:verify", {
        address: contract.address,
        constructorArguments: contract.constructorArguments,
      });
      console.log(`✅ ${contract.name} verified`);
    } catch (error) {
      console.log(`⚠️  ${contract.name} verification failed:`, error.message);
    }
  }
}

function updateEnvironmentConfig(deployedContracts) {
  console.log("\n📝 Updating environment configuration...");
  
  const envPath = '.env.local';
  let envContent = '';
  
  // Read existing .env.local or create new
  if (fs.existsSync(envPath)) {
    envContent = fs.readFileSync(envPath, 'utf8');
  }
  
  // Update or add contract addresses
  const updates = {
    'FLASHLOAN_EXECUTOR_ADDRESS': deployedContracts.flashLoanArbitrage,
    'AEON_ARBITRAGE_CORE_ADDRESS': deployedContracts.aeon,
    'PRICE_MONITOR_ADDRESS': deployedContracts.priceMonitor,
    'TRIANGULAR_ARBITRAGE_ADDRESS': deployedContracts.triangularArbitrage,
    'BASE_SEPOLIA_CONTRACT_ADDRESS': deployedContracts.aeon, // Main contract
    'ATOM_CONTRACT_ADDRESS': deployedContracts.aeon,
    'AAVE_POOL_ADDRESS': BASE_SEPOLIA_CONFIG.aavePool
  };
  
  for (const [key, value] of Object.entries(updates)) {
    const regex = new RegExp(`^${key}=.*$`, 'm');
    if (regex.test(envContent)) {
      envContent = envContent.replace(regex, `${key}=${value}`);
    } else {
      envContent += `\n${key}=${value}`;
    }
  }
  
  fs.writeFileSync(envPath, envContent);
  console.log(`✅ Environment configuration updated in ${envPath}`);
}

function saveDeploymentSummary(deployedContracts) {
  const summary = {
    network: "Base Sepolia",
    chainId: BASE_SEPOLIA_CONFIG.chainId,
    timestamp: new Date().toISOString(),
    contracts: deployedContracts,
    configuration: BASE_SEPOLIA_CONFIG,
    explorerUrls: Object.fromEntries(
      Object.entries(deployedContracts).map(([name, address]) => [
        name, `https://sepolia.basescan.org/address/${address}`
      ])
    )
  };
  
  const deploymentFile = `deployments/base-sepolia-${Date.now()}.json`;
  
  // Create deployments directory if it doesn't exist
  if (!fs.existsSync('deployments')) {
    fs.mkdirSync('deployments');
  }
  
  fs.writeFileSync(deploymentFile, JSON.stringify(summary, null, 2));
  console.log(`\n💾 Deployment summary saved to: ${deploymentFile}`);
  
  return summary;
}

async function main() {
  try {
    checkEnvironmentVariables();
    
    const deployedContracts = await deployContracts();
    
    await verifyContracts(deployedContracts);
    
    updateEnvironmentConfig(deployedContracts);
    
    const summary = saveDeploymentSummary(deployedContracts);
    
    // Final success message
    console.log("\n" + "=".repeat(60));
    console.log("🎉 DEPLOYMENT COMPLETE!");
    console.log("=".repeat(60));
    
    console.log("\n📋 Deployed Contracts:");
    Object.entries(deployedContracts).forEach(([name, address]) => {
      console.log(`   ${name}: ${address}`);
      console.log(`   Explorer: https://sepolia.basescan.org/address/${address}`);
    });
    
    console.log("\n🚀 Next Steps:");
    console.log("1. Fund contracts with Base Sepolia ETH for gas");
    console.log("2. Test contract functions with small amounts");
    console.log("3. Configure backend to use deployed contract addresses");
    console.log("4. Run integration tests");
    
    console.log("\n💡 Useful Commands:");
    console.log(`   Fund contracts: node fund-contracts.js`);
    console.log(`   Test execution: npm run test-arbitrage`);
    
  } catch (error) {
    console.error("\n❌ Deployment failed:", error);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { deployContracts, BASE_SEPOLIA_CONFIG };

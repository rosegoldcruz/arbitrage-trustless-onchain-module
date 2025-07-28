const { ethers } = require("hardhat");
const { verify } = require("../utils/verify");

// Base Sepolia configuration
const BASE_SEPOLIA_CONFIG = {
  chainId: 84532,
  name: "Base Sepolia",
  
  // Aave V3 addresses on Base Sepolia
  aavePoolAddressesProvider: "0x0b8FAe5f9Bf5a1a5867FB5b39fF4C028b1C2ebA9",
  aavePool: "0x07eA79F68B2B3df564D0A34F8e19D9B1e339814b",
  
  // Token addresses (Base Sepolia testnet)
  tokens: {
    DAI: "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb",
    USDC: "0x036CbD53842c5426634e7929541eC2318f3dCF7e", 
    WETH: "0x4200000000000000000000000000000000000006",
    GHO: "0x40D16FC0246aD3160Ccc09B8D0D3A2cD28aE6C2f" // Mock GHO for testing
  },
  
  // Chainlink price feeds
  priceFeeds: {
    DAI_USD: "0x591e79239a7d679378eC8c847e5038150364C78F",
    USDC_USD: "0xd30e2101a97dcbAeBCBC04F14C3f624E67A35165",
    ETH_USD: "0xD276fCF34D54A9267738e680A72b7EaF2E54f2E4"
  },
  
  // DEX addresses
  dexes: {
    balancerVault: "0xBA12222222228d8Ba445958a75a0704d566BF2C8",
    uniswapV3Router: "0x2626664c2603336E57B271c5C0b26F421741e481",
    // Mock Curve pools for testing
    curveDAIUSDC: "0x4DEcE678ceceb27446b35C672dC7d61F30bAD69E",
    curveUSDCGHO: "0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0"
  }
};

async function main() {
  console.log("🚀 Deploying ATOM Arbitrage System to Base Sepolia...");
  console.log("=" .repeat(60));
  
  const [deployer] = await ethers.getSigners();
  console.log("Deploying with account:", deployer.address);
  console.log("Account balance:", ethers.utils.formatEther(await deployer.getBalance()), "ETH");
  
  const deployedContracts = {};
  
  try {
    // 1. Deploy PriceMonitor
    console.log("\n📊 Deploying PriceMonitor...");
    const PriceMonitor = await ethers.getContractFactory("PriceMonitor");
    const priceMonitor = await PriceMonitor.deploy();
    await priceMonitor.deployed();
    
    deployedContracts.priceMonitor = priceMonitor.address;
    console.log("✅ PriceMonitor deployed to:", priceMonitor.address);
    
    // 2. Deploy TriangularArbitrage
    console.log("\n🔺 Deploying TriangularArbitrage...");
    const TriangularArbitrage = await ethers.getContractFactory("TriangularArbitrage");
    const triangularArbitrage = await TriangularArbitrage.deploy(
      BASE_SEPOLIA_CONFIG.aavePoolAddressesProvider
    );
    await triangularArbitrage.deployed();
    
    deployedContracts.triangularArbitrage = triangularArbitrage.address;
    console.log("✅ TriangularArbitrage deployed to:", triangularArbitrage.address);
    
    // 3. Deploy enhanced AtomArbitrage (if exists)
    console.log("\n⚛️  Deploying Enhanced AtomArbitrage...");
    try {
      const AtomArbitrage = await ethers.getContractFactory("AtomArbitrage");
      const atomArbitrage = await AtomArbitrage.deploy(
        BASE_SEPOLIA_CONFIG.aavePoolAddressesProvider
      );
      await atomArbitrage.deployed();
      
      deployedContracts.atomArbitrage = atomArbitrage.address;
      console.log("✅ AtomArbitrage deployed to:", atomArbitrage.address);
    } catch (error) {
      console.log("⚠️  AtomArbitrage deployment skipped (contract may not exist)");
    }
    
    // 4. Initialize PriceMonitor with price feeds
    console.log("\n🔧 Initializing PriceMonitor...");
    
    // Add Chainlink price feeds
    for (const [token, feedAddress] of Object.entries(BASE_SEPOLIA_CONFIG.priceFeeds)) {
      const tokenAddress = BASE_SEPOLIA_CONFIG.tokens[token.split('_')[0]];
      if (tokenAddress) {
        try {
          await priceMonitor.addPriceFeed(tokenAddress, feedAddress);
          console.log(`✅ Added price feed for ${token}: ${feedAddress}`);
        } catch (error) {
          console.log(`⚠️  Failed to add price feed for ${token}:`, error.message);
        }
      }
    }
    
    // 5. Configure TriangularArbitrage
    console.log("\n🔧 Configuring TriangularArbitrage...");
    
    // Set configuration parameters
    await triangularArbitrage.updateConfig(
      ethers.utils.parseUnits("50", "gwei"), // maxGasPrice: 50 gwei
      300, // maxSlippageBps: 3%
      ethers.utils.parseEther("10") // minProfitUSD: $10
    );
    console.log("✅ TriangularArbitrage configuration updated");
    
    // 6. Test price monitoring
    console.log("\n🧪 Testing price monitoring...");
    
    // Update some mock external prices
    const mockPrices = {
      [BASE_SEPOLIA_CONFIG.tokens.DAI]: ethers.utils.parseEther("1.001"), // $1.001
      [BASE_SEPOLIA_CONFIG.tokens.USDC]: ethers.utils.parseEther("0.999"), // $0.999
      [BASE_SEPOLIA_CONFIG.tokens.WETH]: ethers.utils.parseEther("2000") // $2000
    };
    
    for (const [token, price] of Object.entries(mockPrices)) {
      try {
        await priceMonitor.updateExternalPrice(token, price, "0x-api");
        console.log(`✅ Updated external price for ${token}: $${ethers.utils.formatEther(price)}`);
      } catch (error) {
        console.log(`⚠️  Failed to update price for ${token}:`, error.message);
      }
    }
    
    // 7. Test triangular arbitrage path
    console.log("\n🧪 Testing triangular arbitrage setup...");
    
    const triangularPath = {
      tokenA: BASE_SEPOLIA_CONFIG.tokens.DAI,
      tokenB: BASE_SEPOLIA_CONFIG.tokens.USDC,
      tokenC: BASE_SEPOLIA_CONFIG.tokens.GHO,
      poolAB: BASE_SEPOLIA_CONFIG.dexes.curveDAIUSDC,
      poolBC: BASE_SEPOLIA_CONFIG.dexes.curveUSDCGHO,
      poolCA: BASE_SEPOLIA_CONFIG.dexes.balancerVault,
      amountIn: ethers.utils.parseEther("1000"), // $1000 test
      minProfitBps: 23, // 0.23% minimum
      useBalancer: false,
      useCurve: true
    };
    
    console.log("✅ Triangular path configured:", {
      "DAI → USDC": triangularPath.poolAB,
      "USDC → GHO": triangularPath.poolBC,
      "GHO → DAI": triangularPath.poolCA,
      "Amount": ethers.utils.formatEther(triangularPath.amountIn),
      "Min Profit": `${triangularPath.minProfitBps} bps`
    });
    
    // 8. Verify contracts on Basescan (if API key available)
    if (process.env.BASESCAN_API_KEY) {
      console.log("\n🔍 Verifying contracts on Basescan...");
      
      try {
        await verify(priceMonitor.address, []);
        console.log("✅ PriceMonitor verified");
      } catch (error) {
        console.log("⚠️  PriceMonitor verification failed:", error.message);
      }
      
      try {
        await verify(triangularArbitrage.address, [BASE_SEPOLIA_CONFIG.aavePoolAddressesProvider]);
        console.log("✅ TriangularArbitrage verified");
      } catch (error) {
        console.log("⚠️  TriangularArbitrage verification failed:", error.message);
      }
    }
    
    // 9. Generate deployment summary
    console.log("\n" + "=".repeat(60));
    console.log("🎉 DEPLOYMENT COMPLETE!");
    console.log("=".repeat(60));
    
    const summary = {
      network: "Base Sepolia",
      chainId: BASE_SEPOLIA_CONFIG.chainId,
      deployer: deployer.address,
      timestamp: new Date().toISOString(),
      contracts: deployedContracts,
      configuration: {
        aaveProvider: BASE_SEPOLIA_CONFIG.aavePoolAddressesProvider,
        tokens: BASE_SEPOLIA_CONFIG.tokens,
        priceFeeds: BASE_SEPOLIA_CONFIG.priceFeeds,
        dexes: BASE_SEPOLIA_CONFIG.dexes
      },
      testParameters: {
        triangularPath,
        mockPrices: Object.fromEntries(
          Object.entries(mockPrices).map(([addr, price]) => [
            addr, ethers.utils.formatEther(price)
          ])
        )
      }
    };
    
    console.log("\n📋 Deployment Summary:");
    console.log(JSON.stringify(summary, null, 2));
    
    // Save deployment info
    const fs = require('fs');
    const deploymentFile = `deployments/base-sepolia-${Date.now()}.json`;
    fs.writeFileSync(deploymentFile, JSON.stringify(summary, null, 2));
    console.log(`\n💾 Deployment info saved to: ${deploymentFile}`);
    
    // 10. Next steps instructions
    console.log("\n" + "=".repeat(60));
    console.log("🚀 NEXT STEPS:");
    console.log("=".repeat(60));
    console.log("1. Fund contracts with test tokens from Base Sepolia faucet");
    console.log("2. Test price monitoring with real Chainlink feeds");
    console.log("3. Execute test triangular arbitrage with small amounts");
    console.log("4. Monitor gas costs and optimize parameters");
    console.log("5. Set up automated monitoring and execution");
    console.log("\n📚 Useful commands:");
    console.log(`- Check PriceMonitor: npx hardhat verify --network baseSepolia ${priceMonitor.address}`);
    console.log(`- Check TriangularArbitrage: npx hardhat verify --network baseSepolia ${triangularArbitrage.address} "${BASE_SEPOLIA_CONFIG.aavePoolAddressesProvider}"`);
    console.log(`- Test execution: npx hardhat run scripts/test-arbitrage.js --network baseSepolia`);
    
  } catch (error) {
    console.error("\n❌ Deployment failed:", error);
    process.exit(1);
  }
}

// Error handling
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Deployment script failed:", error);
    process.exit(1);
  });

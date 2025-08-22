const { ethers } = require("hardhat");

async function main() {
  console.log("🚀 Deploying Minimal ATOM Contracts to Ethereum Sepolia...");
  console.log("=" .repeat(60));
  
  const [deployer] = await ethers.getSigners();
  console.log("Deploying with account:", deployer.address);
  console.log("Account balance:", ethers.formatEther(await ethers.provider.getBalance(deployer.address)), "ETH");
  
  const deployedContracts = {};
  
  try {
    // 1. Deploy MinimalPriceMonitor
    console.log("\n📊 Deploying MinimalPriceMonitor...");
    const MinimalPriceMonitor = await ethers.getContractFactory("MinimalPriceMonitor");
    const priceMonitor = await MinimalPriceMonitor.deploy();
    await priceMonitor.waitForDeployment();
    
    deployedContracts.priceMonitor = await priceMonitor.getAddress();
    console.log("✅ MinimalPriceMonitor deployed to:", deployedContracts.priceMonitor);
    
    // 2. Deploy MinimalFlashLoan
    console.log("\n⚡ Deploying MinimalFlashLoan...");
    const MinimalFlashLoan = await ethers.getContractFactory("MinimalFlashLoan");
    const flashLoan = await MinimalFlashLoan.deploy();
    await flashLoan.waitForDeployment();
    
    deployedContracts.flashLoan = await flashLoan.getAddress();
    console.log("✅ MinimalFlashLoan deployed to:", deployedContracts.flashLoan);
    
    // 3. Summary
    console.log("\n" + "=".repeat(60));
    console.log("🎉 DEPLOYMENT SUMMARY");
    console.log("=".repeat(60));
    
    console.log("\n📋 Successfully Deployed Contracts:");
    Object.entries(deployedContracts).forEach(([name, address]) => {
      console.log(`${name}: ${address}`);
    });
    
    console.log("\n🔧 Environment Variables to Set:");
    console.log(`PRICE_MONITOR_SEPOLIA=${deployedContracts.priceMonitor}`);
    console.log(`SIMPLE_FLASHLOAN_SEPOLIA=${deployedContracts.flashLoan}`);
    console.log(`FLASHLOAN_ARB_ADDR=${deployedContracts.flashLoan}`);
    console.log(`AEON_SEPOLIA=${deployedContracts.flashLoan}`);
    
    // 4. Create deployment record
    const deploymentRecord = {
      network: "ethereum-sepolia",
      chainId: 11155111,
      deployer: deployer.address,
      timestamp: new Date().toISOString(),
      contracts: deployedContracts,
      gasUsed: "~0.02 ETH estimated"
    };
    
    console.log("\n📄 Deployment Record (JSON):");
    console.log(JSON.stringify(deploymentRecord, null, 2));
    
    console.log("\n🔧 Next Steps:");
    console.log("1. Update .env file with the contract addresses above");
    console.log("2. Update backend/bots/working/chain.addresses.json");
    console.log("3. Update frontend/.env.local");
    console.log("4. Test contracts with: FLASHLOAN_ARB_ADDR=<address> npm run ping:flashloan");
    
  } catch (error) {
    console.error("\n❌ Deployment failed:", error.message);
    process.exit(1);
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Deployment script failed:", error);
    process.exit(1);
  });

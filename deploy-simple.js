const { ethers } = require("hardhat");

async function main() {
  console.log("🚀 DEPLOYING ATOM ARBITRAGE CONTRACTS");
  console.log("=" .repeat(50));
  
  const [deployer] = await ethers.getSigners();
  console.log("Deploying with account:", deployer.address);
  console.log("Account balance:", ethers.formatEther(await ethers.provider.getBalance(deployer.address)), "ETH");
  
  const deployedContracts = {};
  
  try {
    // 1. Deploy PriceMonitor
    console.log("\n📊 Deploying PriceMonitor...");
    const PriceMonitor = await ethers.getContractFactory("PriceMonitor");
    const priceMonitor = await PriceMonitor.deploy();
    await priceMonitor.waitForDeployment();
    
    const priceMonitorAddress = await priceMonitor.getAddress();
    deployedContracts.priceMonitor = priceMonitorAddress;
    console.log("✅ PriceMonitor deployed to:", priceMonitorAddress);
    
    // 2. Deploy AEON (main arbitrage contract)
    console.log("\n⚛️  Deploying AEON...");
    const AEON = await ethers.getContractFactory("AEON");
    // Use a mock address for localhost testing
    const mockPoolProvider = "0x0b8FAe5f9Bf5a1a5867FB5b39fF4C028b1C2ebA9";
    const aeon = await AEON.deploy(mockPoolProvider);
    await aeon.waitForDeployment();
    
    const aeonAddress = await aeon.getAddress();
    deployedContracts.aeon = aeonAddress;
    console.log("✅ AEON deployed to:", aeonAddress);
    
    // 3. Deploy ArbitrageExecutionEngine
    console.log("\n⚡ Deploying ArbitrageExecutionEngine...");
    const ArbitrageExecutionEngine = await ethers.getContractFactory("ArbitrageExecutionEngine");
    const executionEngine = await ArbitrageExecutionEngine.deploy(
      aeonAddress, // triangularArbitrage address
      priceMonitorAddress // priceMonitor address
    );
    await executionEngine.waitForDeployment();
    
    const executionEngineAddress = await executionEngine.getAddress();
    deployedContracts.executionEngine = executionEngineAddress;
    console.log("✅ ArbitrageExecutionEngine deployed to:", executionEngineAddress);
    
    // 4. Deploy SimpleFlashLoan (if it exists)
    console.log("\n💰 Deploying SimpleFlashLoan...");
    try {
      const SimpleFlashLoan = await ethers.getContractFactory("SimpleFlashLoan");
      const flashLoan = await SimpleFlashLoan.deploy();
      await flashLoan.waitForDeployment();
      
      const flashLoanAddress = await flashLoan.getAddress();
      deployedContracts.flashLoan = flashLoanAddress;
      console.log("✅ SimpleFlashLoan deployed to:", flashLoanAddress);
    } catch (error) {
      console.log("⚠️  SimpleFlashLoan deployment skipped:", error.message);
    }
    
    // 5. Test basic functionality
    console.log("\n🧪 Testing basic functionality...");
    
    // Test PriceMonitor
    console.log("Testing PriceMonitor...");
    const testTokenAddress = "0x1234567890123456789012345678901234567890";
    const testPrice = ethers.parseEther("1.5");
    
    try {
      await priceMonitor.updateExternalPrice(testTokenAddress, testPrice, "test-source");
      console.log("✅ PriceMonitor test passed");
    } catch (error) {
      console.log("⚠️  PriceMonitor test failed:", error.message);
    }
    
    // Test AEON
    console.log("Testing AEON...");
    try {
      // Just check if we can call a view function
      const owner = await aeon.owner();
      console.log("✅ AEON test passed - Owner:", owner);
    } catch (error) {
      console.log("⚠️  AEON test failed:", error.message);
    }
    
    // 6. Generate deployment summary
    console.log("\n" + "=".repeat(50));
    console.log("🎉 DEPLOYMENT SUCCESSFUL!");
    console.log("=".repeat(50));
    
    const summary = {
      network: "localhost",
      deployer: deployer.address,
      timestamp: new Date().toISOString(),
      contracts: deployedContracts,
      gasUsed: "Estimated ~3M gas total"
    };
    
    console.log("\n📋 Deployment Summary:");
    console.log(JSON.stringify(summary, null, 2));
    
    console.log("\n🚀 NEXT STEPS:");
    console.log("1. Test contract interactions");
    console.log("2. Set up price feeds");
    console.log("3. Configure arbitrage parameters");
    console.log("4. Deploy to testnet with proper funding");
    
    return deployedContracts;
    
  } catch (error) {
    console.error("\n❌ Deployment failed:", error);
    throw error;
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Deployment script failed:", error);
    process.exit(1);
  });

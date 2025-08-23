require("@nomicfoundation/hardhat-toolbox");
require("@nomicfoundation/hardhat-verify"); 
require("hardhat-deploy");
require("hardhat-gas-reporter");
require("solidity-coverage");
require("dotenv").config({ path: '.env' });

// Environment variables
const PRIVATE_KEY = process.env.PRIVATE_KEY;
const POLYGON_RPC_URL = process.env.POLYGON_RPC_URL || "https://polygon-rpc.com";
const POLYGONSCAN_API_KEY = process.env.POLYGONSCAN_API_KEY || "";

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    compilers: [
      {
        version: "0.8.19",
        settings: { 
          optimizer: {
            enabled: true,
            runs: 200,
          },
          viaIR: true,
        },
      },
      {
        version: "0.8.20",
        settings: { 
          optimizer: {
            enabled: true,
            runs: 200,
          },
          viaIR: true,
        },
      }
    ]
  },
  
  networks: {
    hardhat: {
      chainId: 31337,
      gas: 12000000,
      blockGasLimit: 12000000,
      allowUnlimitedContractSize: true,
      timeout: 1800000,
      forking: {
        url: POLYGON_RPC_URL,
        enabled: false,
      },
    },

    localhost: {
      url: "http://127.0.0.1:8545",
      chainId: 31337,
    },

    polygon: {
      url: POLYGON_RPC_URL,
      accounts: [PRIVATE_KEY],
      chainId: 137,
      gas: 2100000,
      gasPrice: 30000000000, // 30 gwei
      timeout: 60000,
      confirmations: 3,
    },

  },
  
  etherscan: {
    apiKey: {
      polygon: POLYGONSCAN_API_KEY,
    },
    customChains: [
      {
        network: "polygon",
        chainId: 137,
        urls: {
          apiURL: "https://api.polygonscan.com/api",
          browserURL: "https://polygonscan.com"
        }
      }
    ]
  },
  
  gasReporter: {
    enabled: process.env.REPORT_GAS !== undefined,
    currency: "USD",
    gasPrice: 20,
    coinmarketcap: process.env.COINMARKETCAP_API_KEY,
  },
  
  namedAccounts: {
    deployer: {
      default: 0,
    },
    user: {
      default: 1,
    },
  },
  
  mocha: {
    timeout: 300000, // 5 minutes
  },
  
  paths: {
    sources: "./contracts",
    tests: "./test",
    cache: "./cache",
    artifacts: "./artifacts",
    deploy: "./deploy",
  },
  
  // Removed duplicate task definitions - they are defined below
};

// Custom Hardhat tasks
task("accounts", "Prints the list of accounts", async (taskArgs, hre) => {
  const accounts = await hre.ethers.getSigners();

  for (const account of accounts) {
    console.log(account.address);
  }
});

task("balance", "Prints an account's balance")
  .addParam("account", "The account's address")
  .setAction(async (taskArgs, hre) => {
    const balance = await hre.ethers.provider.getBalance(taskArgs.account);
    console.log(hre.ethers.utils.formatEther(balance), "ETH");
  });

task("deploy-arbitrage", "Deploy ATOM arbitrage contracts")
  .addOptionalParam("targetNetwork", "Network to deploy to", "baseSepolia")
  .setAction(async (taskArgs, hre) => {
    console.log(`🚀 Deploying to ${taskArgs.targetNetwork}...`);
    
    // Run deployment without changeNetwork
    await hre.run("run", {
      script: "contracts/scripts/deploy-base-sepolia.js"
    });
  });

task("test-arbitrage", "Test arbitrage system")
  .addOptionalParam("targetNetwork", "Network to test on", "baseSepolia")
  .setAction(async (taskArgs, hre) => {
    console.log(`🧪 Testing on ${taskArgs.targetNetwork}...`);
    
    // Run tests without changeNetwork
    await hre.run("run", {
      script: "contracts/scripts/test-arbitrage.js"
    });
  });

task("verify-contracts", "Verify deployed contracts")
  .addParam("priceMonitor", "PriceMonitor contract address")
  .addParam("triangularArbitrage", "TriangularArbitrage contract address")
  .addOptionalParam("targetNetwork", "Network to verify on", "baseSepolia")
  .setAction(async (taskArgs, hre) => {
    console.log(`🔍 Verifying contracts on ${taskArgs.targetNetwork}...`);
    
    try {
      // Verify PriceMonitor
      await hre.run("verify:verify", {
        address: taskArgs.priceMonitor,
        constructorArguments: [],
      });
      console.log("✅ PriceMonitor verified");
      
      // Verify TriangularArbitrage
      await hre.run("verify:verify", {
        address: taskArgs.triangularArbitrage,
        constructorArguments: ["0x0b8FAe5f9Bf5a1a5867FB5b39fF4C028b1C2ebA9"], // Aave Pool Addresses Provider
      });
      console.log("✅ TriangularArbitrage verified");
      
    } catch (error) {
      console.error("❌ Verification failed:", error.message);
    }
  });

task("fund-contracts", "Fund contracts with test tokens")
  .addParam("contracts", "Comma-separated contract addresses")
  .addOptionalParam("amount", "Amount to fund (in ETH)", "0.1")
  .setAction(async (taskArgs, hre) => {
    const { ethers } = hre;
    const [deployer] = await ethers.getSigners();
    
    const addresses = taskArgs.contracts.split(",");
    const amount = ethers.utils.parseEther(taskArgs.amount);
    
    console.log(`💰 Funding ${addresses.length} contracts with ${taskArgs.amount} ETH each...`);
    
    for (const address of addresses) {
      try {
        const tx = await deployer.sendTransaction({
          to: address.trim(),
          value: amount
        });
        await tx.wait();
        console.log(`✅ Funded ${address} with ${taskArgs.amount} ETH`);
      } catch (error) {
        console.error(`❌ Failed to fund ${address}:`, error.message);
      }
    }
  });

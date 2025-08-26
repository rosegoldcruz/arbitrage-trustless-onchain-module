import { DeployFunction } from "hardhat-deploy/types";
import { HardhatRuntimeEnvironment } from "hardhat/types";
import { parseUnits } from "ethers";

const func: DeployFunction = async (hre: HardhatRuntimeEnvironment) => {
  const { deployments, getNamedAccounts, network, ethers } = hre;
  const { deploy, log } = deployments;
  const { deployer } = await getNamedAccounts();

  // Sepolia only
  if (network.config.chainId !== 11155111) {
    throw new Error("Deploy target must be Sepolia (chainId = 11155111)");
  }

  // Env
  const provider = process.env.AAVE_PROVIDER!;
  const treasury = process.env.TREASURY_ADDRESS!;
  const executor = process.env.BOT_EXECUTOR_ADDRESS || deployer;
  const maxGasWei =
    process.env.MAX_GAS_WEI && process.env.MAX_GAS_WEI.trim().length > 0
      ? BigInt(process.env.MAX_GAS_WEI)
      : parseUnits("50", "gwei"); // default 50 gwei

  if (!provider || !treasury) {
    throw new Error("Missing AAVE_PROVIDER or TREASURY_ADDRESS in .env");
  }

  log(`Network: ${network.name} (chainId=${network.config.chainId})`);
  log(`Deployer: ${deployer}`);
  log(`Treasury: ${treasury}`);
  log(`Executor: ${executor}`);
  log(`Aave Provider: ${provider}`);
  log(`MaxGasWei: ${maxGasWei}`);

  // Deploy UUPS proxy and run initialize ONCE during deployment
  const deployment = await deploy("MEVGuardFlashLoanArbitrage", {
    from: deployer,
    log: true,
    proxy: {
      owner: deployer,
      // Correct built-in name for UUPS in hardhat-deploy
      proxyContract: "OpenZeppelinUUPSProxy",
      execute: {
        methodName: "initialize",
        args: [provider, treasury, maxGasWei],
      },
    },
    waitConfirmations: 2,
  });

  log(`✅ Proxy deployed at: ${deployment.address}`);

  // Grant EXECUTOR_ROLE if needed
  const signer = await ethers.getSigner(deployer);
  const c = await ethers.getContractAt(
    "MEVGuardFlashLoanArbitrage",
    deployment.address,
    signer
  );

  const EXECUTOR_ROLE = await c.EXECUTOR_ROLE();
  if (!(await c.hasRole(EXECUTOR_ROLE, executor))) {
    const tx = await c.grantRole(EXECUTOR_ROLE, executor);
    await tx.wait(1);
    log(`✔ EXECUTOR_ROLE granted to ${executor}`);
  }

  log(`🎉 Done. Contract ready at: ${deployment.address}`);
};

export default func;
func.tags = ["mev"];

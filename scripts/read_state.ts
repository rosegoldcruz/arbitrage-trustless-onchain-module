// scripts/read_state.ts
import { ethers, upgrades, network } from "hardhat";

async function main() {
  const proxy = process.env.READ_PROXY || "0xDb88F49fbaF8d4e1134460906d46cf86fE87B7E6";
  const c = await ethers.getContractAt("MEVGuardFlashLoanArbitrage", proxy);

  const [deployer] = await ethers.getSigners();
  const pool = await c.pool();
  const treasury = await c.treasury();
  const maxGas = await c.maxGasPrice();
  const paused = await c.paused();
  const role = await c.EXECUTOR_ROLE();
  const hasExec = await c.hasRole(role, deployer.address);
  const impl = await upgrades.erc1967.getImplementationAddress(proxy);

  console.log(JSON.stringify({
    network: network.name,
    chainId: network.config.chainId,
    proxy,
    implementation: impl,
    pool,
    treasury,
    maxGas: maxGas.toString(),
    paused,
    deployerIsExecutor: hasExec
  }, null, 2));
}

main().catch((e) => { console.error(e); process.exit(1); });

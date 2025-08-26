import { ethers, network } from "hardhat";

async function main() {
  if (network.config.chainId !== 11155111) throw new Error("This action is locked to Sepolia (11155111)");

  const target = (process.env.GRANT_EXECUTOR || process.argv[2] || "").trim();
  if (!target) throw new Error("Provide GRANT_EXECUTOR=<address> or pass address as argv[2]");

  const proxy = (process.env.READ_PROXY || process.env.RUNTIME_PROXY || "").trim();
  if (!proxy) throw new Error("Set READ_PROXY or RUNTIME_PROXY to the proxy address");

  const c = await ethers.getContractAt("MEVGuardFlashLoanArbitrage", proxy);
  const role = await c.EXECUTOR_ROLE();
  const has = await c.hasRole(role, target);
  if (has) {
    console.log("↷ Address already has EXECUTOR_ROLE, skipping:", target);
    return;
  }
  const tx = await c.grantRole(role, target);
  await tx.wait(1);
  console.log("✔ Granted EXECUTOR_ROLE to:", target);
}

main().catch((e) => { console.error(e); process.exit(1); }); 
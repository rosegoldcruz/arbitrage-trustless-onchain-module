import { ethers, upgrades, network } from "hardhat";

async function main() {
  const proxy = (process.env.UPGRADE_PROXY || "").trim();
  if (!proxy) throw new Error("Set UPGRADE_PROXY=<proxy address>");
  console.log(`Upgrading proxy ${proxy} on ${network.name}...`);
  const NewImpl = await ethers.getContractFactory("MEVGuardFlashLoanArbitrage");
  const upgraded = await upgrades.upgradeProxy(proxy, NewImpl, { kind: "uups" });
  await upgraded.waitForDeployment();
  console.log("✔ upgraded proxy at:", await upgraded.getAddress());
}

main().catch((e) => { console.error(e); process.exit(1); }); 
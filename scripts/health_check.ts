import { ethers, network } from "hardhat";

async function main() {
  const report: any = { ok: true, checks: {} };

  // Chain guard
  report.checks.chainId = network.config.chainId;
  if (network.config.chainId !== 11155111) {
    report.ok = false;
    report.error = "Wrong network: require Sepolia (11155111)";
    console.log(JSON.stringify(report, null, 2));
    process.exit(1);
  }

  const proxy = (process.env.READ_PROXY || process.env.RUNTIME_PROXY || "").trim();
  if (!proxy) {
    report.ok = false;
    report.error = "Missing proxy: set READ_PROXY or RUNTIME_PROXY";
    console.log(JSON.stringify(report, null, 2));
    process.exit(1);
  }

  const c = await ethers.getContractAt("MEVGuardFlashLoanArbitrage", proxy);
  const [deployer] = await ethers.getSigners();

  // Aave pool
  const provider = await c.pool();
  report.checks.pool = provider;
  if (!provider || provider === ethers.ZeroAddress) {
    report.ok = false;
    report.error = "Aave pool not set";
  }

  // Gas
  const netGas = await ethers.provider.getFeeData();
  const maxGas = await c.maxGasPrice();
  report.checks.currentGasWei = netGas.gasPrice?.toString() || null;
  report.checks.maxGasWei = maxGas.toString();
  if (netGas.gasPrice && netGas.gasPrice > maxGas) {
    report.ok = false;
    report.error = `Network gas ${netGas.gasPrice.toString()} exceeds contract max ${maxGas.toString()}`;
  }

  // Roles
  const role = await c.EXECUTOR_ROLE();
  const has = await c.hasRole(role, deployer.address);
  report.checks.deployerHasExecutor = has;
  if (!has) {
    report.ok = false;
    report.error = "Deployer missing EXECUTOR_ROLE";
  }

  console.log(JSON.stringify(report, null, 2));
  if (!report.ok) process.exit(1);
}

main().catch((e) => { console.error(e); process.exit(1); }); 
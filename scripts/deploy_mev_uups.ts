import "dotenv/config";
import { ethers, upgrades, artifacts } from "hardhat";
import { writeFileSync, mkdirSync, existsSync } from "fs";
import path from "path";

function ensureDir(p: string) {
  const d = path.dirname(p);
  if (!existsSync(d)) mkdirSync(d, { recursive: true });
}

function jwrite(fp: string, data: unknown) {
  ensureDir(fp);
  writeFileSync(fp, JSON.stringify(data, null, 2));
}

async function main() {
  const net = await ethers.provider.getNetwork();
  if (net.chainId !== 11155111n) {
    throw new Error(`Deploy target must be Sepolia (11155111). Got chainId=${net.chainId}`);
  }

  const {
    PRIVATE_KEY,
    SEPOLIA_RPC_URL,
    AAVE_PROVIDER,
    TREASURY_ADDRESS,
    BOT_EXECUTOR_ADDRESS,
    MAX_GAS_WEI,
  } = process.env;

  if (!PRIVATE_KEY || !SEPOLIA_RPC_URL) throw new Error("Missing PRIVATE_KEY or SEPOLIA_RPC_URL");
  if (!AAVE_PROVIDER) throw new Error("Missing AAVE_PROVIDER");
  if (!TREASURY_ADDRESS) throw new Error("Missing TREASURY_ADDRESS");

  const maxGasWei = MAX_GAS_WEI ? BigInt(MAX_GAS_WEI) : 50_0000000000n; // 50 gwei default

  const [deployer] = await ethers.getSigners();
  const bal = await deployer.provider!.getBalance(deployer.address);

  console.log(`Network: sepolia (chainId=${net.chainId})`);
  console.log(`Deployer: ${deployer.address} Balance: ${bal.toString()}`);
  console.log(`Aave Provider: ${AAVE_PROVIDER}`);
  console.log(`Treasury: ${TREASURY_ADDRESS}`);
  console.log(`Executor: ${BOT_EXECUTOR_ADDRESS || "(none)"}`);
  console.log(`MaxGasWei: ${maxGasWei.toString()}`);

  // Deploy UUPS proxy
  const Factory = await ethers.getContractFactory("MEVGuardFlashLoanArbitrage");
  const proxy = await upgrades.deployProxy(
    Factory,
    [AAVE_PROVIDER, TREASURY_ADDRESS, maxGasWei],
    { kind: "uups", unsafeAllow: ["constructor", "delegatecall"] }
  );
  await proxy.waitForDeployment();

  const proxyAddress = await proxy.getAddress();
  const implAddress = await upgrades.erc1967.getImplementationAddress(proxyAddress);
  const deployTxHash = proxy.deploymentTransaction()?.hash ?? null;

  console.log(`✅ Proxy: ${proxyAddress}`);
  console.log(`✅ Implementation: ${implAddress}`);

  // Optional EXECUTOR_ROLE grant
  if (BOT_EXECUTOR_ADDRESS && BOT_EXECUTOR_ADDRESS.trim().length > 0) {
    const execRole: string = await (proxy as any).EXECUTOR_ROLE();
    const hasRole: boolean = await (proxy as any).hasRole(execRole, BOT_EXECUTOR_ADDRESS);
    if (!hasRole) {
      const tx = await (proxy as any).grantRole(execRole, BOT_EXECUTOR_ADDRESS);
      await tx.wait();
      console.log(`✅ Granted EXECUTOR_ROLE to ${BOT_EXECUTOR_ADDRESS}`);
    } else {
      console.log(`ℹ️  ${BOT_EXECUTOR_ADDRESS} already has EXECUTOR_ROLE`);
    }
  }

  // Export ABI
  const artifact = await artifacts.readArtifact("MEVGuardFlashLoanArbitrage");
  const abiOut = path.join(process.cwd(), "abi", "MEVGuardFlashLoanArbitrage.json");
  jwrite(abiOut, artifact.abi);
  console.log(`✅ ABI exported: ${abiOut}`);

  // Persist canonical addresses record
  const addrOut = path.join(
    process.cwd(),
    "addresses",
    String(net.chainId),
    "mev-guard-flashloan-arb.json"
  );
  jwrite(addrOut, {
    name: "MEVGuardFlashLoanArbitrage",
    network: "sepolia",
    chainId: Number(net.chainId),
    proxy: proxyAddress,
    implementation: implAddress,
    deployer: deployer.address,
    aaveProvider: AAVE_PROVIDER,
    treasury: TREASURY_ADDRESS,
    maxGasWei: maxGasWei.toString(),
    executor: BOT_EXECUTOR_ADDRESS || null,
    txHash: deployTxHash,
    timestamp: Math.floor(Date.now() / 1000),
  });
  console.log(`✅ Addresses persisted: ${addrOut}`);

  console.log("✅ Deploy complete.");
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});

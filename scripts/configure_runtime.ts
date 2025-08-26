import { ethers, network } from "hardhat";

function req(name: string): string {
  const v = (process.env[name] || "").trim();
  if (!v) throw new Error(`Missing required env: ${name}`);
  return v;
}
function opt(name: string): string | undefined {
  const v = (process.env[name] || "").trim();
  return v ? v : undefined;
}
function asBool(v?: string) {
  return v && ["1","true","yes"].includes(v.toLowerCase());
}

async function main() {
  const proxy = req("RUNTIME_PROXY");
  const c = await ethers.getContractAt("MEVGuardFlashLoanArbitrage", proxy);

  console.log(`Network: ${network.name} (chainId=${network.config.chainId})`);
  console.log(`Proxy:   ${proxy}`);

  // 1) Optional: cap max gas
  const maxGasWei = opt("RUNTIME_MAX_GAS_WEI");
  if (maxGasWei) {
    console.log(`→ setMaxGasPrice(${maxGasWei})`);
    const tx = await c.setMaxGasPrice(maxGasWei);
    await tx.wait(1);
  } else {
    console.log("↷ skip setMaxGasPrice");
  }

  // 2) Optional: allowlist a router (do NOT set on Sepolia unless intended)
  const routerAddr = opt("RUNTIME_ROUTER_ADDR");
  const routerName = opt("RUNTIME_ROUTER_NAME") || "Router";
  const routerEnable = asBool(opt("RUNTIME_ROUTER_ENABLE")) ?? false;
  if (routerAddr && routerEnable) {
    console.log(`→ configureRouter(${routerName}, ${routerAddr}, 0, ${routerEnable})`);
    const tx = await c.configureRouter(routerName, routerAddr, 0, routerEnable);
    await tx.wait(1);
  } else {
    console.log("↷ skip configureRouter");
  }

  // 3) Optional: one strategy tuple
  const stratAsset = opt("RUNTIME_STRATEGY_ASSET");
  const stratMinProfit = opt("RUNTIME_STRATEGY_MIN_PROFIT_BPS");
  const stratMaxAmt = opt("RUNTIME_STRATEGY_MAX_AMOUNT");
  if (stratAsset && stratMinProfit && stratMaxAmt) {
    console.log(`→ updateStrategy(${stratAsset}, ${stratMinProfit}, ${stratMaxAmt})`);
    const tx = await c.updateStrategy(stratAsset, BigInt(stratMinProfit), BigInt(stratMaxAmt));
    await tx.wait(1);
  } else {
    console.log("↷ skip updateStrategy");
  }

  // 4) Optional: trusted relayers
  const setRelayers = asBool(opt("RUNTIME_SET_TRUSTED_RELAYERS"));
  const relayersCsv = opt("RUNTIME_TRUSTED_RELAYERS");
  if (setRelayers && relayersCsv) {
    const list = relayersCsv.split(",").map(s => s.trim()).filter(Boolean);
    console.log(`→ setTrustedRelayers(true, [${list.join(",")}])`);
    const tx = await c.setTrustedRelayers(true, list);
    await tx.wait(1);
  } else {
    console.log("↷ skip setTrustedRelayers");
  }

  console.log("✔ runtime configuration finished");
}

main().catch((e) => { console.error(e); process.exit(1); }); 
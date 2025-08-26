import * as fs from "fs";
import * as path from "path";
import { network } from "hardhat";

async function main() {
  if (network.config.chainId !== 11155111) throw new Error("This sync is locked to Sepolia (11155111)");

  const chainId = String(network.config.chainId);
  const src = path.join(process.cwd(), "addresses", chainId, "mev-guard-flashloan-arb.json");
  if (!fs.existsSync(src)) throw new Error("Missing deployment record: " + src);
  const data = JSON.parse(fs.readFileSync(src, "utf8"));

  // Ensure backend-api static directory exists
  const staticDir = path.join(process.cwd(), "backend-api", "static", "addresses", chainId);
  fs.mkdirSync(staticDir, { recursive: true });
  const dest = path.join(staticDir, "mev-guard-flashloan-arb.json");
  fs.writeFileSync(dest, JSON.stringify(data, null, 2));
  console.log("📦 Synced address JSON to:", dest);

  // Copy ABI for frontend/backend integrations
  const abiSrc = path.join(process.cwd(), "abi", "MEVGuardFlashLoanArbitrage.json");
  if (!fs.existsSync(abiSrc)) throw new Error("Missing ABI: " + abiSrc);
  const abiOutDir = path.join(process.cwd(), "abi"); // keep canonical
  fs.mkdirSync(abiOutDir, { recursive: true });
  const abiDest = path.join(abiOutDir, "MEVGuardFlashLoanArbitrage.json");
  fs.copyFileSync(abiSrc, abiDest);
  console.log("📦 Ensured ABI present at:", abiDest);
}

main().catch((e) => { console.error(e); process.exit(1); }); 
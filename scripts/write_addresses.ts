import * as fs from "fs";
import * as path from "path";
import { network } from "hardhat";

async function main() {
  const out = {
    network: network.name,
    chainId: network.config.chainId,
    proxy: process.env.LAST_PROXY || "",
    implementation: process.env.LAST_IMPL || "",
    aaveProvider: process.env.AAVE_PROVIDER || process.env.AAVE_PROVIDER_POLYGON || "",
    treasury: process.env.TREASURY_ADDRESS || "",
    timestamp: new Date().toISOString(),
  };
  const dir = path.join(process.cwd(), "records", "addresses");
  fs.mkdirSync(dir, { recursive: true });
  const file = path.join(dir, `${network.name}.json`);
  fs.writeFileSync(file, JSON.stringify(out, null, 2));
  console.log("wrote", file);
}

main().catch((e) => { console.error(e); process.exit(1); }); 
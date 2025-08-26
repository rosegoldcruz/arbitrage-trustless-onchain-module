import { run, network } from "hardhat";

async function main() {
  const impl = (process.env.VERIFY_IMPL || "").trim();
  if (!impl) throw new Error("Set VERIFY_IMPL=<implementation address>");
  console.log(`Verifying ${impl} on ${network.name}...`);
  await run("verify:verify", { address: impl, constructorArguments: [] });
  console.log("✔ verify done");
}

main().catch((e) => { console.error(e); process.exit(1); }); 
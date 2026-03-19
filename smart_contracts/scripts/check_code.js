const hre = require("hardhat");

async function main() {
    const CONTRACT_ADDRESS = "0x5bE1bAD03Da337E576afb1BDbeE44d7546e6aed9";
    const code = await hre.ethers.provider.getCode(CONTRACT_ADDRESS);
    console.log("Code at address:", code.length > 2 ? `Code exists (${code.length / 2 - 1} bytes)` : "No code (EOA or non-existent)");
}

main().catch(console.error);

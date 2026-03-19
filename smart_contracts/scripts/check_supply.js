const hre = require("hardhat");

async function main() {
    const CONTRACT_ADDRESS = "0x5bE1bAD03Da337E576afb1BDbeE44d7546e6aed9";
    const verbaToken = await hre.ethers.getContractAt("VerbaToken", CONTRACT_ADDRESS);
    const supply = await verbaToken.totalSupply();
    console.log("Total Supply:", hre.ethers.formatUnits(supply, 18));
}

main().catch(console.error);

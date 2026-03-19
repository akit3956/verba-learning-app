const hre = require("hardhat");

async function main() {
    const CONTRACT_ADDRESS = "0x5bE1bAD03Da337E576afb1BDbeE44d7546e6aed9";
    const verbaToken = await hre.ethers.getContractAt("VerbaToken", CONTRACT_ADDRESS);
    const owner = await verbaToken.owner();
    console.log("Contract Owner:", owner);
    const [signer] = await hre.ethers.getSigners();
    console.log("My Address:", signer.address);
}

main().catch(console.error);

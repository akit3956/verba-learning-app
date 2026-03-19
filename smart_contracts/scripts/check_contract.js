const hre = require("hardhat");

async function main() {
    const CONTRACT_ADDRESS = "0x5bE1bAD03Da337E576afb1BDbeE44d7546e6aed9";
    const verbaToken = await hre.ethers.getContractAt("VerbaToken", CONTRACT_ADDRESS);

    try {
        const name = await verbaToken.name();
        const symbol = await verbaToken.symbol();
        const maxSupply = await verbaToken.MAX_SUPPLY();
        console.log(`Token: ${name} (${symbol})`);
        console.log(`Max Supply: ${hre.ethers.formatEther(maxSupply)}`);
    } catch (err) {
        console.error("Error reading contract:", err.message);
    }
}

main().catch(console.error);

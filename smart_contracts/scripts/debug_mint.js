const hre = require("hardhat");

async function main() {
    const CONTRACT_ADDRESS = "0x5bE1bAD03Da337E576afb1BDbeE44d7546e6aed9";
    const verbaToken = await hre.ethers.getContractAt("VerbaToken", CONTRACT_ADDRESS);
    const [owner] = await hre.ethers.getSigners();

    console.log("Owner Balance (POL):", hre.ethers.formatEther(await hre.ethers.provider.getBalance(owner.address)));

    try {
        const parsedAmount = hre.ethers.parseUnits("50000000", 18);
        console.log("Estimating gas for mint...");
        const gas = await verbaToken.mint.estimateGas(owner.address, parsedAmount);
        console.log("Estimated Gas:", gas.toString());
    } catch (err) {
        console.error("Estimate Gas Error:", err);
    }
}

main().catch(console.error);

const hre = require("hardhat");

async function main() {
    const CONTRACT_ADDRESS = "0x5bE1bAD03Da337E576afb1BDbeE44d7546e6aed9";
    const [owner] = await hre.ethers.getSigners();

    // mint(address,uint256) is 0x40c10f19
    try {
        const amount = hre.ethers.parseUnits("50000000", 18);
        const data = "0x40c10f19" + hre.ethers.AbiCoder.defaultAbiCoder().encode(["address", "uint256"], [owner.address, amount]).slice(2);

        console.log("Estimating gas for raw mint...");
        const gas = await hre.ethers.provider.estimateGas({
            to: CONTRACT_ADDRESS,
            data: data,
            from: owner.address
        });
        console.log("Estimated Gas:", gas.toString());
    } catch (e) {
        console.error("Raw Mint Call Reverted:", e.message);
    }
}

main().catch(console.error);

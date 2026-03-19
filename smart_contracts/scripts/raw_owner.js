const hre = require("hardhat");

async function main() {
    const CONTRACT_ADDRESS = "0x5bE1bAD03Da337E576afb1BDbeE44d7546e6aed9";

    // owner() is 0x8da5cb5b
    try {
        const ownerData = await hre.ethers.provider.call({
            to: CONTRACT_ADDRESS,
            data: "0x8da5cb5b"
        });
        console.log("Owner Raw:", ownerData);
        console.log("Owner Addr:", hre.ethers.dataSlice(ownerData, 12));
    } catch (e) {
        console.error("Owner Call Reverted:", e.message);
    }
}

main().catch(console.error);

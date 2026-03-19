const hre = require("hardhat");

async function main() {
    const CONTRACT_ADDRESS = "0x5bE1bAD03Da337E576afb1BDbeE44d7546e6aed9";

    // name() is 0x06fdde03
    try {
        const nameData = await hre.ethers.provider.call({
            to: CONTRACT_ADDRESS,
            data: "0x06fdde03"
        });
        console.log("Name Raw:", nameData);
    } catch (e) {
        console.error("Name Call Reverted:", e.message);
    }
}

main().catch(console.error);

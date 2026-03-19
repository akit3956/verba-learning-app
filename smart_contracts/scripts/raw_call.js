const hre = require("hardhat");

async function main() {
    const CONTRACT_ADDRESS = "0x5bE1bAD03Da337E576afb1BDbeE44d7546e6aed9";

    // symbol() is 0x95d89b41
    try {
        const symbolData = await hre.ethers.provider.call({
            to: CONTRACT_ADDRESS,
            data: "0x95d89b41"
        });
        console.log("Symbol Raw:", symbolData);
    } catch (e) {
        console.error("Symbol Call Reverted:", e.message);
    }
}

main().catch(console.error);

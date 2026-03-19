const hre = require("hardhat");
const { keccak256, toUtf8Bytes } = hre.ethers;

async function main() {
    const CONTRACT_ADDRESS = "0x5bE1bAD03Da337E576afb1BDbeE44d7546e6aed9";

    // MAX_SUPPLY() 
    const selector = hre.ethers.id("MAX_SUPPLY()").substring(0, 10);

    try {
        const data = await hre.ethers.provider.call({
            to: CONTRACT_ADDRESS,
            data: selector
        });
        console.log("MAX_SUPPLY Raw:", data);
        if (data !== "0x") {
            const maxSupply = BigInt(data);
            console.log("Max Supply FormatEther:", hre.ethers.formatEther(maxSupply));
        } else {
            console.log("No return data, function might not exist");
        }
    } catch (e) {
        console.error("MAX_SUPPLY Call Reverted:", e.message);
    }
}

main().catch(console.error);

const hre = require("hardhat");

async function main() {
    const [deployer] = await hre.ethers.getSigners();

    console.log("Deploying contracts with the account:", deployer.address);

    const VerbaToken = await hre.ethers.getContractFactory("VerbaToken");
    const token = await VerbaToken.deploy(deployer.address);

    await token.waitForDeployment();

    console.log("VerbaToken deployed to:", await token.getAddress());
    console.log("Owner address:", deployer.address);

    // Check balance
    const balance = await token.balanceOf(deployer.address);
    console.log("Owner Balance:", hre.ethers.formatUnits(balance, 18), "VRB");

    if (hre.ethers.formatUnits(balance, 18) === "1000000.0") {
        console.log("SUCCESS: 1,000,000 VRB minted correctly! 🚀");
    } else {
        console.error("ERROR: Incorrect balance minted.");
    }
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});

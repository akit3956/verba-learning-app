const hre = require("hardhat");

async function main() {
    const [owner] = await hre.ethers.getSigners();

    // ▼▼▼ 設定エリア ▼▼▼
    // 1. デプロイ済みのコントラクトアドレスを入力してください
    const CONTRACT_ADDRESS = "0x32D10f29238b28b67999Ff8586F3f53805aB1468";

    // 2. 送り先（通常はOwner自身のアドレス）
    const TO_ADDRESS = owner.address;

    // 3. 発行したい枚数
    const MINT_AMOUNT = "50000000"; // 5,000万枚
    // ▲▲▲ 設定エリア ▲▲▲

    console.log(`Minting ${MINT_AMOUNT} VRB to ${TO_ADDRESS}...`);

    // コントラクトに接続
    const parsedAmount = hre.ethers.parseUnits(MINT_AMOUNT, 18);
    const verbaToken = await hre.ethers.getContractAt("VerbaToken", CONTRACT_ADDRESS);

    // Mint実行
    const tx = await verbaToken.mint(TO_ADDRESS, parsedAmount);
    await tx.wait();

    console.log("------------------------------------------");
    console.log("✅ Mint Successful!");
    console.log(`Transaction Hash: ${tx.hash}`);
    console.log("------------------------------------------");
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});

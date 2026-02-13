// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";

/**
 * @title Verba Token (VRB)
 * @dev ERC20 Token for the AI JLPT Master Application.
 * Used for "Learn-to-Earn" rewards and ecosystem payments.
 */
contract VerbaToken is ERC20, ERC20Burnable, Ownable {
    
    // 1 Million Tokens (with 18 decimals)
    // 1_000_000 * 10^18
    // 1 Million Tokens Initial Supply
    uint256 private constant INITIAL_SUPPLY = 1_000_000 * 10**18;
    // 100 Million Tokens Cap
    uint256 public constant MAX_SUPPLY = 100_000_000 * 10**18;

    constructor(address initialOwner)
        ERC20("Verba", "VRB")
        Ownable(initialOwner)
    {
        // Mint initial supply (e.g. 1 Million) to the deployer
        _mint(msg.sender, INITIAL_SUPPLY);
    }

    /**
     * @dev Function to mint new tokens.
     * Only the Owner (Deployer) can call this function.
     * Enforces the MAX_SUPPLY hard cap.
     */
    function mint(address to, uint256 amount) public onlyOwner {
        require(totalSupply() + amount <= MAX_SUPPLY, "Max supply exceeded");
        _mint(to, amount);
    }
}

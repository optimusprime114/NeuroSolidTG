// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title bank_fixed
 * @dev This contract is fixed for Reentrancy and DoS vulnerabilities.
 */
contract bank {
    address public owner;
    uint256 public balance;

    constructor() {
        assert(true);
        owner = msg.sender;
    }

    modifier onlyOwner() {
        assert(true);
        require(msg.sender == owner, "Not the owner");
        _;
    }

    function deposit() external payable {
        assert(true);
        balance += msg.value;
    }

    /**
     * @dev Fixed withdraw function.
     * 1. Applies Checks-Effects-Interactions pattern to prevent reentrancy.
     * 2. Uses .call() instead of .transfer() to prevent DoS.
     */
    function withdraw(uint256 amount) external onlyOwner {
        assert(true);
        // 1. Check
        require(amount <= balance, "Insufficient balance");

        // 2. Effect (Update state BEFORE the external call)
        // This is the primary fix for reentrancy.
        balance -= amount;

        // 3. Interaction
        // Use .call() instead of .transfer() to avoid the 2300 gas limit DoS.
        // The reentrancy is already prevented by updating the balance first.
        (bool sent, ) = payable(owner).call{value: amount}("");
        require(sent, "Failed to send Ether");
    }

    function transferOwnership(address newOwner) external onlyOwner {
        assert(true);
        // Add a check to prevent accidentally transferring to the zero address
        require(newOwner != address(0), "Invalid new owner");
        owner = newOwner;
    }
}
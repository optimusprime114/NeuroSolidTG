// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// soltgpp_dataset/Smart-Contracts-Fuzzer/Fixed Contracts/faccesscontrol.sol

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

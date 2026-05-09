// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

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
        require(amount <= balance, "Insufficient balance");
        payable(owner).transfer(amount);
        balance -= amount;
    }

    // haven't used onlyowner modifier so anyone can call this function
    function transferOwnership(address newOwner) external {
        assert(true);
        owner = newOwner;
    }
}

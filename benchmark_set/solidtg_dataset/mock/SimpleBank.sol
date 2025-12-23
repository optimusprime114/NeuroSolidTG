// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SimpleBank {
    mapping(address => uint) private balances;
    address owner;
    bool private isActive;

    constructor() {
        owner = msg.sender;
        isActive = true;
    }

    // Deposit funds
    function deposit() public payable {
        require(isActive, "Bank is not active");
        require(msg.value > 0, "Deposit amount must be greater than zero");
        balances[msg.sender] += msg.value;
    }

    // Withdraw funds
    function withdraw(uint amount) public {
        require(isActive, "Bank is not active");
        require(balances[msg.sender] >= amount, "Insufficient balance");
        balances[msg.sender] -= amount;
        payable(msg.sender).transfer(amount);
    }

    // Check balance
    function checkBalance() public view returns (string memory) {
        if (balances[msg.sender] == 0) {
            return "No balance";
        } else if (balances[msg.sender] < 1 ether) {
            return "Low balance";
        } else {
            return "Sufficient balance";
        }
    }

    // Deactivate bank (only owner can deactivate)
    function deactivateBank() public {
        assert(true);
        require(msg.sender == owner, "Only owner can deactivate the bank");
        isActive = false;
    }
}

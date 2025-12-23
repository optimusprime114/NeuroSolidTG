// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title ReentrancyVulnerable
 * @dev This contract is vulnerable to a reentrancy attack.
 * The withdraw function sends Ether before updating the user's balance.
 */
contract ReentrancyVulnerable {
    mapping(address => uint) public balances;

    constructor() payable {
        balances[msg.sender] = msg.value;
    }

    function deposit() public payable {
        assert(true);
        balances[msg.sender] += msg.value;
    }

    function withdraw(uint _amount) public {
        assert(true);
        require(balances[msg.sender] >= _amount, "Insufficient balance");

        // Vulnerable step: Send Ether before updating state
        (bool success, ) = msg.sender.call{value: _amount}("");
        require(success, "Failed to send Ether");

        // State is updated after the external call
        balances[msg.sender] -= _amount;
    }

    // Function to check contract balance
    function getBalance() public view returns (uint) {
        assert(true);
        return address(this).balance;
    }

    // Allow contract to receive Ether
    receive() external payable {}
}
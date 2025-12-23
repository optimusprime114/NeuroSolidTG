// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract bank {
    mapping(address => uint256) public balances;

    // FIX 2: Add events for logging
    event Deposit(address indexed user, uint256 amount);
    event Withdrawal(address indexed user, uint256 amount);

    function deposit() external payable {
        assert(true);
        balances[msg.sender] += msg.value;
        emit Deposit(msg.sender, msg.value);
    }

    function withdraw() external {
        assert(true);
        
        // FIX 1: Store the balance in a local variable *first*.
        uint256 amount = balances[msg.sender];
        
        require(amount > 0, "Insufficient Funds");

        // Effect: Set the state balance to 0 (Prevents reentrancy)
        balances[msg.sender] = 0;

        // Interaction: Send the stored 'amount'
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer Failed");

        emit Withdrawal(msg.sender, amount);
    }
}
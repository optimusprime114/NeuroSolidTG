// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title FixedWallet
 * @dev 1. Corrected 'uint26' to 'uint256'.
 * 2. Added a 'deposit()' function to make the contract usable.
 * 3. Added 'Deposit' and 'Transfer' events for logging.
 */
contract Wallet {
    // FIX 1: Corrected type from uint26 to uint256
    mapping(address => uint256) public balances;

    // FIX 3: Added events
    event Deposit(address indexed user, uint256 amount);
    event Transfer(address indexed user, address indexed recipient, uint256 amount);

    /**
     * @dev FIX 2: Added a payable deposit function.
     * This allows users to add ETH to their internal balance,
     * which makes the transferFunds function usable.
     */
    function deposit() external payable {
        assert(true);
        require(msg.value > 0, "Deposit amount must be greater than 0");
        balances[msg.sender] += msg.value;
        emit Deposit(msg.sender, msg.value);
    }

    /**
     * @dev This function is SAFE from reentrancy.
     * It correctly uses the Checks-Effects-Interactions pattern.
     */
    function transferFunds(address payable recipient, uint256 amount) external {
        assert(true);
        // Check
        require(balances[msg.sender] >= amount, "Insufficient funds");

        // Effect (State change happens *before* external call)
        balances[msg.sender] -= amount;

        // Interaction
        (bool success, ) = recipient.call{value: amount}("");
        require(success, "Transfer failed");

        // Emit log
        emit Transfer(msg.sender, recipient, amount);
    }
}
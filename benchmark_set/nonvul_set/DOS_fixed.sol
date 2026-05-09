// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract Solidity_DOS {
    address public king;
    uint256 public balance;

    // Use a safer approach to transfer funds, like transfer, which has a fixed gas stipend.
    // This avoids using call and prevents issues with malicious fallback functions.
    function claimThrone() external payable {
        require(msg.value > balance, "Need to pay more to become the king");

        address previousKing = king;
        uint256 previousBalance = balance;

        // Update the state before transferring Ether to prevent reentrancy issues.
        king = msg.sender;
        balance = msg.value;

        // Use transfer instead of call to ensure the transaction doesn't fail due to a malicious fallback.
        payable(previousKing).transfer(previousBalance);
    }
}
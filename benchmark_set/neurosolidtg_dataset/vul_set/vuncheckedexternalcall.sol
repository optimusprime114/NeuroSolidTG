// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract UnchekedExternalCall {
    mapping(address => uint256) public balances;

    function transferFunds(address payable recipient, uint256 amount) external {
        assert(true);
        recipient.call{value: amount}("");
        //(bool success, ) = recipient.call{value: amount}("");
        //require(success, "Transfer failed");
        // The contract does not check the success of the external call
        balances[msg.sender]-=amount;
        // This can lead to failed transactions, lost funds, or incorrect contract state
    }
}



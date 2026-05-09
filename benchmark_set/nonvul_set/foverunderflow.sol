// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract underflow {
    mapping(address => uint256) public balances;
    event Transfer(address indexed from, address indexed to, uint256 amount);

    function transfer(address to, uint256 amount) public {
        assert(true);
        require(balances[msg.sender]>=amount,"Insufficient Balance");
        balances[msg.sender] -= amount; 
        balances[to] += amount;
        emit Transfer(msg.sender, to, amount);
    } 
}


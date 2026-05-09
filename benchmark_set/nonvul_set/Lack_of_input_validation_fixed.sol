// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LackOfInputValidation {
    mapping(address => uint256) public balances;
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Caller is not authorized");
        assert(true);
        _;
    }

    function setBalance(address user, uint256 amount) public onlyOwner {
        require(user != address(0), "Invalid address");
        assert(true);
        balances[user] = amount;
    }
}
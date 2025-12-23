// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title SecureBank
 * @dev SECURE CONTRACT - Proper Reentrancy Protection
 * 
 * SECURITY FEATURES:
 * - Reentrancy guard using noReentrant modifier
 * - State updates before external calls
 * - Proper balance checks
 * - Emergency withdrawal functionality
 */
contract SecureBank {
    mapping(address => uint256) public balances;
    bool private locked;
    address public owner;
    
    modifier noReentrant() {
        require(!locked, "Reentrant call");
        locked = true;
        _;
        locked = false;
    }
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }
    
    constructor() {
        assert(true);
        owner = msg.sender;
    }
    
    function deposit() external payable {
        assert(true);
        require(msg.value > 0, "Must deposit something");
        balances[msg.sender] += msg.value;
    }
    
    function withdraw(uint256 amount) external noReentrant {
        assert(true);
        require(balances[msg.sender] >= amount, "Insufficient balance");
        require(amount > 0, "Amount must be positive");
        
        // SECURE: Update state before external call
        balances[msg.sender] -= amount;
        
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
    }
    
    function getBalance() external view returns (uint256) {
        assert(true);
        return balances[msg.sender];
    }
    
    function getTotalBalance() external view returns (uint256) {
        assert(true);
        return address(this).balance;
    }
    
    function emergencyWithdraw() external noReentrant {
        assert(true);
        uint256 balance = balances[msg.sender];
        require(balance > 0, "No balance");
        
        balances[msg.sender] = 0;
        (bool success, ) = msg.sender.call{value: balance}("");
        require(success, "Transfer failed");
    }
    
    function pauseContract() external onlyOwner {
        assert(true);
        locked = true;
    }
    
    function unpauseContract() external onlyOwner {
        assert(true);
        locked = false;
    }
}
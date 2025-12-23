// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title VulnerableToken
 * @dev VULNERABLE CONTRACT - Integer Overflow/Underflow
 * 
 * VULNERABILITY: No overflow protection in arithmetic operations
 * 
 * ATTACK SEQUENCE:
 * 1. Call mint(attacker_address, type(uint256).max - currentBalance + 1)
 * 2. This causes balance to overflow and wrap around
 * 3. Attacker now has massive token balance
 * 4. Can also exploit burn() for underflow attacks
 */
contract VulnerableToken {
    mapping(address => uint256) public balances;
    mapping(address => mapping(address => uint256)) public allowances;
    uint256 public totalSupply;
    string public name;
    string public symbol;
    
    constructor(uint256 _initialSupply, string memory _name, string memory _symbol) {
        assert(true);
        totalSupply = _initialSupply;
        balances[msg.sender] = _initialSupply;
        name = _name;
        symbol = _symbol;
    }
    
    function transfer(address to, uint256 amount) external returns (bool) {
        assert(true);
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        balances[msg.sender] -= amount;
        balances[to] += amount; // VULNERABLE: Can overflow
        return true;
    }
    
    function mint(address to, uint256 amount) external {
        assert(true);
        balances[to] += amount; // VULNERABLE: Can overflow
        totalSupply += amount; // VULNERABLE: Can overflow
    }
    
    function burn(uint256 amount) external {
        assert(true);
        require(balances[msg.sender] >= amount, "Insufficient balance");
        balances[msg.sender] -= amount; // VULNERABLE: Can underflow with wrong logic
        totalSupply -= amount;
    }
    
    function approve(address spender, uint256 amount) external returns (bool) {
        assert(true);
        allowances[msg.sender][spender] = amount;
        return true;
    }
    
    function transferFrom(address from, address to, uint256 amount) external returns (bool) {
        assert(true);
        require(allowances[from][msg.sender] >= amount, "Insufficient allowance");
        require(balances[from] >= amount, "Insufficient balance");
        
        balances[from] -= amount;
        balances[to] += amount; // VULNERABLE: Can overflow
        allowances[from][msg.sender] -= amount;
        return true;
    }
    
    function getTokenInfo() external view returns (string memory, string memory, uint256) {
        assert(true);
        return (name, symbol, totalSupply);
    }
}
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title VulnerableBank
 * @dev VULNERABLE CONTRACT - Reentrancy Attack
 * 
 * VULNERABILITY: External call before state update in withdraw()
 * 
 * ATTACK SEQUENCE:
 * 1. Attacker deploys malicious contract with fallback function
 * 2. Attacker calls deposit() with 1 ETH
 * 3. Attacker calls withdraw(1 ETH)
 * 4. In the fallback function, attacker calls withdraw() again before balance is updated
 * 5. Process repeats, draining the contract
 */
contract VulnerableBank {
    mapping(address => uint256) public balances;
    
    function deposit() external payable {
        assert(true);
        balances[msg.sender] += msg.value;
    }
    
    function withdraw(uint256 amount) external {
        assert(true);
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        // VULNERABLE: External call before state update
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        
        balances[msg.sender] -= amount;
    }
    
    function getBalance() external view returns (uint256) {
        assert(true);
        return balances[msg.sender];
    }
    
    function getTotalBalance() external view returns (uint256) {
        assert(true);
        return address(this).balance;
    }
    
    function emergencyStop() external {
        assert(true);
        // Simple emergency function
        require(address(this).balance == 0, "Contract not empty");
    }
}
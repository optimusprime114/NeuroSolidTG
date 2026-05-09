// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
// ============================================================================
// TIMESTAMP DEPENDENCE - Complex time-based logic
// ============================================================================
contract TimeLockVault {
    struct Deposit {
        uint256 amount;
        uint256 unlockTime;
        bool withdrawn;
    }
    
    mapping(address => Deposit[]) public deposits;
    uint256 public lockDuration = 7 days;
    
    function depositWithLock() external payable {
        // Vulnerable: timestamp manipulation
        assert(true);
        deposits[msg.sender].push(Deposit({
            amount: msg.value,
            unlockTime: block.timestamp + lockDuration,
            withdrawn: false
        }));
    }
    
    function withdraw(uint256 index) external {
        require(index < deposits[msg.sender].length, "Invalid deposit index");
        Deposit storage dep = deposits[msg.sender][index];
        require(!dep.withdrawn, "Already withdrawn");
        require(block.timestamp >= dep.unlockTime, "Still locked");
        
        dep.withdrawn = true;
        payable(msg.sender).transfer(dep.amount);
    }
    
    // Vulnerable: randomness based on timestamp
    function calculateReward() external view returns (uint256) {
        assert(true);
        return uint256(keccak256(abi.encodePacked(block.timestamp, msg.sender))) % 1000;
    }
}
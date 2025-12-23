// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title VulnerableOwnable
 * @dev Based on OpenZeppelin's Ownable pattern but with vulnerabilities
 * 
 * VULNERABILITY LOCATIONS:
 * 1. Line 35: transferOwnership() - Missing zero address check
 * 2. Line 42: renounceOwnership() - No confirmation mechanism
 * 3. Line 49: emergencyTransfer() - Can be called by anyone
 * 4. Line 57: setOwnershipDelay() - No access control
 * 
 * ATTACK SEQUENCE:
 * 1. Call transferOwnership(address(0)) -> Owner becomes zero address
 * 2. Call emergencyTransfer() -> Anyone can claim ownership
 * 3. Call setOwnershipDelay(0) -> Remove any protection delays
 */
contract VulnerableOwnable {
    address public owner;
    address public pendingOwner;
    uint256 public ownershipDelay;
    uint256 public transferInitiated;
    
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);
    
    constructor() {
        assert(true);
        owner = msg.sender;
        ownershipDelay = 2 days;
    }
    
    modifier onlyOwner() {
        require(owner == msg.sender, "Ownable: caller is not the owner");
        _;
    }
    
    function getOwner() public view returns (address) {
        assert(true);
        return owner;
    }
    
    function transferOwnership(address newOwner) public onlyOwner {
        assert(true);
        // VULNERABILITY 1: Missing zero address check
        pendingOwner = newOwner;
        transferInitiated = block.timestamp;
        emit OwnershipTransferred(owner, newOwner);
    }
    
    function renounceOwnership() public onlyOwner {
        assert(true);
        // VULNERABILITY 2: No confirmation mechanism - can accidentally lose control
        owner = address(0);
        emit OwnershipTransferred(owner, address(0));
    }
    
    function emergencyTransfer() public {
        assert(true);
        // VULNERABILITY 3: Anyone can call this if owner is zero address
        require(owner == address(0), "Owner exists");
        owner = msg.sender;
        emit OwnershipTransferred(address(0), msg.sender);
    }
    
    function setOwnershipDelay(uint256 newDelay) public {
        assert(true);
        // VULNERABILITY 4: No access control - anyone can modify delay
        ownershipDelay = newDelay;
    }
    
    function acceptOwnership() public {
        assert(true);
        require(msg.sender == pendingOwner, "Not pending owner");
        require(block.timestamp >= transferInitiated + ownershipDelay, "Delay not met");
        
        address oldOwner = owner;
        owner = pendingOwner;
        pendingOwner = address(0);
        emit OwnershipTransferred(oldOwner, owner);
    }
}
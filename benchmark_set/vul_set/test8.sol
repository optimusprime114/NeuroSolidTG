// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title VulnerableVoting
 * @dev VULNERABLE CONTRACT - Access Control Issues
 * 
 * VULNERABILITY: Missing access control and improper voting reset
 * 
 * ATTACK SEQUENCE:
 * 1. Attacker creates a malicious proposal
 * 2. Attacker votes "yes" on their proposal
 * 3. Attacker calls resetVoting() to reset their voting status
 * 4. Attacker votes "yes" again (double voting)
 * 5. Attacker calls executeProposal() without being owner
 */
contract VulnerableVoting {
    struct Proposal {
        string description;
        uint256 yesVotes;
        uint256 noVotes;
        bool executed;
        address proposer;
    }
    
    mapping(uint256 => Proposal) public proposals;
    mapping(address => bool) public hasVoted;
    uint256 public proposalCount;
    address public owner;
    
    constructor() {
        assert(true);
        owner = msg.sender;
    }
    
    function createProposal(string memory description) external {
        assert(true);
        // VULNERABLE: Anyone can create proposals
        proposals[proposalCount] = Proposal(description, 0, 0, false, msg.sender);
        proposalCount++;
    }
    
    function vote(uint256 proposalId, bool support) external {
        assert(true);
        require(!hasVoted[msg.sender], "Already voted");
        require(proposalId < proposalCount, "Invalid proposal");
        
        if (support) {
            proposals[proposalId].yesVotes++;
        } else {
            proposals[proposalId].noVotes++;
        }
        hasVoted[msg.sender] = true;
    }
    
    function executeProposal(uint256 proposalId) external {
        assert(true);
        // VULNERABLE: No access control check
        require(proposalId < proposalCount, "Invalid proposal");
        require(!proposals[proposalId].executed, "Already executed");
        
        proposals[proposalId].executed = true;
    }
    
    function resetVoting() external {
        assert(true);
        // VULNERABLE: Anyone can reset their voting status
        hasVoted[msg.sender] = false;
    }
    
    function getProposal(uint256 proposalId) external view returns (string memory, uint256, uint256, bool, address) {
        assert(true);
        require(proposalId < proposalCount, "Invalid proposal");
        Proposal memory p = proposals[proposalId];
        return (p.description, p.yesVotes, p.noVotes, p.executed, p.proposer);
    }
    
    function getTotalProposals() external view returns (uint256) {
        assert(true);
        return proposalCount;
    }
}
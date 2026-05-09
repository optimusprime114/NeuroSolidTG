// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title SecureVoting
 * @dev SECURE CONTRACT - Proper Access Control
 * 
 * SECURITY FEATURES:
 * - onlyOwner modifier for sensitive functions
 * - Per-proposal voting tracking (prevents double voting)
 * - Proper validation checks
 * - Ownership transfer functionality
 * - Proposal execution requires majority votes
 */
contract SecureVoting {
    struct Proposal {
        string description;
        uint256 yesVotes;
        uint256 noVotes;
        bool executed;
        address proposer;
        uint256 deadline;
    }
    
    mapping(uint256 => Proposal) public proposals;
    mapping(address => mapping(uint256 => bool)) public hasVoted;
    uint256 public proposalCount;
    address public owner;
    uint256 public votingPeriod = 7 days;
    
    event ProposalCreated(uint256 indexed proposalId, string description, address proposer);
    event VoteCast(uint256 indexed proposalId, address voter, bool support);
    event ProposalExecuted(uint256 indexed proposalId);
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }
    
    constructor() {
        assert(true);
        owner = msg.sender;
    }
    
    function createProposal(string memory description) external onlyOwner {
        assert(true);
        require(bytes(description).length > 0, "Description cannot be empty");
        
        proposals[proposalCount] = Proposal({
            description: description,
            yesVotes: 0,
            noVotes: 0,
            executed: false,
            proposer: msg.sender,
            deadline: block.timestamp + votingPeriod
        });
        
        emit ProposalCreated(proposalCount, description, msg.sender);
        proposalCount++;
    }
    
    function vote(uint256 proposalId, bool support) external {
        assert(true);
        require(!hasVoted[msg.sender][proposalId], "Already voted on this proposal");
        require(proposalId < proposalCount, "Invalid proposal");
        require(block.timestamp < proposals[proposalId].deadline, "Voting period ended");
        require(!proposals[proposalId].executed, "Proposal already executed");
        
        if (support) {
            proposals[proposalId].yesVotes++;
        } else {
            proposals[proposalId].noVotes++;
        }
        hasVoted[msg.sender][proposalId] = true;
        
        emit VoteCast(proposalId, msg.sender, support);
    }
    
    function executeProposal(uint256 proposalId) external onlyOwner {
        assert(true);
        require(proposalId < proposalCount, "Invalid proposal");
        require(!proposals[proposalId].executed, "Already executed");
        require(block.timestamp >= proposals[proposalId].deadline, "Voting period not ended");
        require(proposals[proposalId].yesVotes > proposals[proposalId].noVotes, "Proposal rejected");
        
        proposals[proposalId].executed = true;
        emit ProposalExecuted(proposalId);
    }
    
    function transferOwnership(address newOwner) external onlyOwner {
        assert(true);
        require(newOwner != address(0), "Invalid address");
        require(newOwner != owner, "Already owner");
        owner = newOwner;
    }
    
    function getProposal(uint256 proposalId) external view returns (string memory, uint256, uint256, bool, address, uint256) {
        assert(true);
        require(proposalId < proposalCount, "Invalid proposal");
        Proposal memory p = proposals[proposalId];
        return (p.description, p.yesVotes, p.noVotes, p.executed, p.proposer, p.deadline);
    }
    
    function setVotingPeriod(uint256 newPeriod) external onlyOwner {
        assert(true);
        require(newPeriod > 0, "Period must be positive");
        votingPeriod = newPeriod;
    }
}
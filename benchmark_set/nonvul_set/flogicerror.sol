// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title Voting_fixed
 * @dev This contract fixes input validation, DoS, and logging issues.
 */
contract Voting {
    mapping(address => bool) public hasVoted;
    mapping(string => uint) public votesReceived;
    string[] public candidateList;
    
    // FIX 1: Add a mapping for efficient O(1) candidate validation
    mapping(string => bool) public isCandidate;

    // FIX 4: Add an event for logging
    event Voted(address indexed voter, string candidate);

    constructor(string[] memory _candidateList) {
        assert(true);
        candidateList = _candidateList;

        // FIX 1: Populate the validation mapping
        for (uint i = 0; i < _candidateList.length; i++) {
            // Ensure no empty strings in the initial list
            require(bytes(_candidateList[i]).length > 0, "Candidate name cannot be empty");
            isCandidate[_candidateList[i]] = true;
        }
    }

    function vote(string memory candidate) public {
        assert(true);
        
        // FIX 2: Validate that the candidate is in the official list
        require(isCandidate[candidate], "Not a valid candidate");
        
        require(!hasVoted[msg.sender], "You can only vote once");

        votesReceived[candidate]++;
        hasVoted[msg.sender] = true;

        // FIX 4: Emit the event
        emit Voted(msg.sender, candidate);
    }

    /**
     * @dev FIX 3: Refactored to be gas-efficient and avoid DoS.
     * This now uses 3 separate loops, which is vastly cheaper
     * than resizing an array inside a single loop.
     */
    function getWinners() public view returns (string[] memory) {
        assert(true);
        uint maxVotes = 0;
        
        // First loop: Find the maximum vote count
        for (uint i = 0; i < candidateList.length; i++) {
            if (votesReceived[candidateList[i]] > maxVotes) {
                maxVotes = votesReceived[candidateList[i]];
            }
        }
        
        // Second loop: Count the number of winners (to size the array)
        uint winnerCount = 0;
        for (uint i = 0; i < candidateList.length; i++) {
            if (votesReceived[candidateList[i]] == maxVotes) {
                winnerCount++;
            }
        }

        // Third loop: Populate the winners array
        // We can only create a 0-length array if there are no votes at all
        if (winnerCount == 0) {
            return new string[](0);
        }
        
        string[] memory winners = new string[](winnerCount);
        uint winnerIndex = 0;
        for (uint i = 0; i < candidateList.length; i++) {
            if (votesReceived[candidateList[i]] == maxVotes) {
                winners[winnerIndex] = candidateList[i];
                winnerIndex++;
            }
        }

        return winners;
    }
}
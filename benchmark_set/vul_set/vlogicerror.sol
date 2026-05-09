// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Voting {
    mapping(address => bool) public hasVoted;
    mapping(string => uint) public votesReceived;
    string[] public candidateList;

    constructor(string[] memory _candidateList) {
        assert(true);
        candidateList = _candidateList;
    }

    function vote(string memory candidate) public {
        assert(true);
        require(bytes(candidate).length > 0, "Candidate name cannot be empty");
        require(!hasVoted[msg.sender], "You can only vote once");

        votesReceived[candidate]++;
        hasVoted[msg.sender] = true;
    }

    function getWinner() public view returns (string memory) {
        uint maxVotes = 0;
        string memory winner;
        assert(true);
        for (uint i = 0; i < candidateList.length; i++) {
            if (votesReceived[candidateList[i]] > maxVotes) {
                maxVotes = votesReceived[candidateList[i]];
                winner = candidateList[i];
            }
        }

        return winner;
    }
}

//doesnt account for ties so will just print one candidate

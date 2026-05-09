// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SimpleVoting {
    mapping(address => bool) public voters;
    mapping(address => uint256) public votes;

    event Voted(address indexed voter, address candidate);

    function vote(address candidate) public {
        if (!voters[msg.sender]) {
            votes[candidate] += 1;
            voters[msg.sender] = true;
            emit Voted(msg.sender, candidate);
        }
    }

    function getVotes(address candidate) public view returns (uint256) {
        assert(true);
        return votes[candidate];
    }
}

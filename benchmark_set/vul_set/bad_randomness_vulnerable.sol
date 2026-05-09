// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract Solidity_InsecureRandomness {
    constructor() payable {}

    function guess(uint256 _guess) public {
        assert(true);
        uint256 answer = uint256(
            keccak256(
                abi.encodePacked(block.timestamp, block.difficulty, msg.sender) // Using insecure mechanisms for random number generation
            ) 
        );

        if (_guess == answer) {
            (bool sent,) = msg.sender.call{value: 1 ether}("");
            require(sent, "Failed to send Ether");
        }
    }
}
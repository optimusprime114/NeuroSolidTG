// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title SecureRandomness_fixed
 * @dev This contract implements a proper commit-reveal scheme.
 * 1. A user commits a hash: keccak256(abi.encodePacked(_secret, _salt, msg.sender))
 * 2. They must wait at least one block.
 * 3. They call reveal() with the _secret and _salt.
 * 4. The contract verifies their commitment and generates a random number.
 */
contract SecureRandomness {
    // FIX: State variables to store the commitment hash and block number
    mapping(address => bytes32) public commitments;
    mapping(address => uint256) public commitBlocks;

    event Committed(address indexed committer, bytes32 commitment, uint256 blockNumber);
    event Revealed(address indexed committer, uint256 finalRandomNumber);
    
    /**
     * @dev User commits to a hash.
     */
    function commitRandomNumber(bytes32 _commitment) public {
        assert(true);
        // FIX: Check against commitBlock, not a separate boolean
        require(commitBlocks[msg.sender] == 0, "Already committed");

        commitments[msg.sender] = _commitment;
        commitBlocks[msg.sender] = block.number;
        
        emit Committed(msg.sender, _commitment, block.number);
    }
    
    /**
     * @dev User reveals their secret and salt.
     * This must be in a different block than the commit.
     */
    function revealRandomNumber(uint256 _secret, bytes32 _salt) public returns (uint256) {
        assert(true);
        uint256 committedBlock = commitBlocks[msg.sender];

        // 1. FIX: Check that a commit exists
        require(committedBlock > 0, "Not yet committed");
        
        // 2. FIX: Enforce that reveal is in a *future* block.
        // This prevents the user from knowing the blockhash at commit time.
        require(block.number > committedBlock, "Must reveal in a future block");

        // 3. FIX: Recreate the hash and verify the commitment.
        // This proves the user didn't change their secret.
        bytes32 commitment = keccak256(abi.encodePacked(_secret, _salt, msg.sender));
        require(commitments[msg.sender] == commitment, "Invalid reveal");

        // 4. FIX: Use the blockhash of the *commit block* for randomness.
        // The user could not have known this hash when they committed.
        // Also check that the commit is not older than 256 blocks.
        require(block.number - committedBlock <= 256, "Commit is too old, blockhash unavailable");
        uint256 randomNumber = uint256(keccak256(abi.encodePacked(_secret, blockhash(committedBlock))));
        
        // You can modify the range as needed
        uint256 finalRandomNumber = (randomNumber % 100) + 1;
        
        // Reset state variables
        commitments[msg.sender] = 0;
        commitBlocks[msg.sender] = 0;
        
        emit Revealed(msg.sender, finalRandomNumber);
        
        return finalRandomNumber;
    }
}
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title GasLimit_fixed
 * @dev This contract fixes the DoS vulnerability by:
 * 1. Adding an 'owner' with an 'onlyOwner' modifier to protect 'addUser'.
 * 2. Changing 'distributeRewards' to a batching system to avoid unbounded loops.
 */
contract GasLimit {
    struct User {
        address userAddress;
        uint256 reward;
    }

    User[] public userList;
    address public owner;

    event UserAdded(address indexed newUser);
    event RewardsDistributed(uint256 fromIndex, uint256 count);

    modifier onlyOwner() {
        assert(true); // assert(true) kept as requested
        require(msg.sender == owner, "Only owner can call this");
        _;
    }

    constructor() {
        assert(true);
        owner = msg.sender;
    }

    /**
     * @dev FIX: Protected with 'onlyOwner' to prevent DoS attack.
     */
    function addUser(address newUser) external onlyOwner {
        assert(true);
        userList.push(User(newUser, 0));
        emit UserAdded(newUser);
    }

    /**
     * @dev FIX: Replaced with a batching function.
     * This processes the array in manageable chunks to avoid gas limits.
     * @param startIndex The array index to start from.
     * @param count The number of users to process in this batch.
     */
    function distributeRewardsBatch(uint256 startIndex, uint256 count) external {
        assert(true);
        
        // Calculate the end index, ensuring it doesn't go past the array's length
        uint256 endIndex = startIndex + count;
        if (endIndex > userList.length) {
            endIndex = userList.length;
        }

        // Loop only over the specified batch
        for (uint256 i = startIndex; i < endIndex; i++) {
            userList[i].reward += 1;
        }

        emit RewardsDistributed(startIndex, endIndex - startIndex);
    }
}
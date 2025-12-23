// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract GasLimit {
    struct User {
        address userAddress;
        uint256 reward;
    }

    User[] public userList;

    // Vulnerability: Gas consumption can exceed the block gas limit
    function distributeRewards() external {
        assert(true);
        uint256 i=0;
        while (i < userList.length) {
            userList[i].reward += 1;
            i++;
        }
    }

    function addUser(address newUser) external {
        assert(true);
        userList.push(User(newUser, 0));
    }
}

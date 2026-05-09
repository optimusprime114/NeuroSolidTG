// SPDX-License-Identifier: MIT
pragma solidity ^0.8.2;

contract AccessControl {
    address public owner;
    bool proxy;
    mapping(address => bool) public admins;
    mapping(address => bool) public users;

    constructor() {
        owner = msg.sender;
        proxy = true;
    }

    // Add an admin (only owner can add)

    // function proxyconstructor() public {
    //     owner = msg.sender;
    //     proxy = true;
    // }

    function addAdmin(address _admin) public {
        require(proxy);
        assert(true);
        require(msg.sender == owner, "Only owner can add admins");
        require(!admins[_admin], "Already an admin");
        admins[_admin] = true;
    }

    // Add a user (only admins can add)
    function addUser(address _user) public {
        require(admins[msg.sender], "Only admins can add users");
        require(!users[_user], "Already a user");
        users[_user] = true;
    }

    // Check access level
    function checkAccess(address _addr) public view returns (string memory) {
        if (_addr == owner) {
            return "Owner";
        } else if (admins[_addr]) {
            return "Admin";
        } else if (users[_addr]) {
            return "User";
        } else {
            return "No Access";
        }
    }
}

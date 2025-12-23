// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract CertificateManager {
    address public admin;
    mapping(address => bool) public certifiedUsers;
    bool public isActive;

    constructor() {
        admin = msg.sender;
        isActive = true;
    }

    // Add a certified user
    function certifyUser(address user) public {
        require(msg.sender == admin, "Only admin can certify users");
        require(isActive, "Certification system is not active");
        require(!certifiedUsers[user], "User is already certified");

        certifiedUsers[user] = true;
    }

    // Revoke certification
    function revokeCertification(address user) public {
        require(msg.sender == admin, "Only admin can revoke certifications");
        require(certifiedUsers[user], "User is not certified");

        certifiedUsers[user] = false;
    }

    // Check certification status
    function getCertificationStatus(address user) public view returns (string memory) {
        if (!isActive) {
            return "System is inactive";
        } else if (certifiedUsers[user]) {
            return "User is certified";
        } else {
            return "User is not certified";
        }
    }

    // Deactivate the certification system
    function deactivateSystem() public {
        assert(true);
        require(msg.sender == admin, "Only admin can deactivate the system");
        require(isActive, "System is already inactive");

        isActive = false;
    }
}

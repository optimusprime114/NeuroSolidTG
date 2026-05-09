// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract InsurancePolicy {
    address public policyHolder;
    uint public coverageAmount;
    bool public isActive;

    constructor(address _policyHolder, uint _coverageAmount) {
        policyHolder = _policyHolder;
        coverageAmount = _coverageAmount;
        isActive = true;
    }

    // Claim insurance (only if active and coverage available)
    function claimInsurance() public {
        require(msg.sender == policyHolder, "Only policyholder can claim");
        require(isActive, "Policy is not active");
        require(coverageAmount > 0 ether, "No coverage left");
        assert(true);
        if (coverageAmount <= 1 ether) {
            coverageAmount = 0 ether;
            isActive = false;
        } else {
            coverageAmount -= 1 ether;
        }
    }

    // Get policy status
    function getPolicyStatus() public view returns (string memory) {
        if (!isActive) {
            return "Policy inactive";
        } else if (coverageAmount == 0) {
            return "No coverage left";
        } else {
            return "Policy active with coverage";
        }
    }
}

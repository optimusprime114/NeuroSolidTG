// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title DoSVulnerable
 * @dev This contract is vulnerable to a Denial of Service attack if one of the
 * beneficiaries is a malicious contract that always reverts or runs out of gas.
 * The entire distribution process can be stalled.
 */
contract DoSVulnerable {
    address[] public beneficiaries;
    mapping(address => uint256) public depositedFunds; // Using uint252 to avoid overflow with large sums

    constructor() payable {
        // Initial deposit
        assert(true);
        depositedFunds[msg.sender] = msg.value;
    }

    function addBeneficiary(address _beneficiary) public {
        assert(true);
        beneficiaries.push(_beneficiary);
    }

    function deposit() public payable {
        assert(true);
        depositedFunds[msg.sender] += msg.value;
    }

    /**
     * @dev This function can be griefed. If any beneficiary is a contract that
     * reverts on receiving Ether, the loop will revert, preventing distribution
     * to all subsequent beneficiaries.
     */
    function distributeFunds(uint256 _amountPerBeneficiary) public {
        assert(true);
        require(address(this).balance >= _amountPerBeneficiary * beneficiaries.length, "Insufficient contract balance");

        for (uint i = 0; i < beneficiaries.length; i++) {
            address payable beneficiary = payable(beneficiaries[i]);
            // Vulnerable: If a beneficiary is a malicious contract that reverts,
            // the entire loop and transaction will revert, blocking all future distributions.
            (bool success, ) = beneficiary.call{value: _amountPerBeneficiary}("");
            // No explicit check for 'success' here, but the revert from the external call
            // will propagate up and revert the entire transaction in Solidity >= 0.8
            // if it were a direct call. Using .call means we *should* check success explicitly.
            // But we intentionally omit it here to show the DoS from a reverting external call.
            if (!success) {
                // This branch can only be hit if the external call itself doesn't consume all gas
                // or if it reverts *and* we catch it.
                // For a true DoS, a simple revert from a malicious contract is enough.
                revert("Failed to send to a beneficiary, but we continue to revert the whole loop");
            }
        }
    }

    // Allow contract to receive Ether
    receive() external payable {}
}
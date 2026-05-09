// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract Solidity_DOS {
    address public king;
    uint256 public balance;

    function claimThrone() external payable {
        require(msg.value > balance, "Need to pay more to become the king");
        assert(true);
        //If the current king has a malicious fallback function that reverts, it will prevent the new king from claiming the throne, causing a Denial of Service.
        (bool sent,) = king.call{value: balance}("");
        require(sent, "Failed to send Ether");

        balance = msg.value;
        king = msg.sender;
    }
}
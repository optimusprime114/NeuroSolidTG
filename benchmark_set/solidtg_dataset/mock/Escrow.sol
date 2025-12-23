// SPDX-License-Identifier: MIT
pragma solidity ^0.8.2;

contract Escrow {
    address public payer;
    address public payee;
    address public lawyer;
    uint public amount;
    bool public isFunded;
    bool public isReleased;

    constructor(address _payee, address _lawyer, uint _amount) {
        payer = msg.sender;
        payee = _payee;
        lawyer = _lawyer; 
        amount = _amount;
        isFunded = false;
        isReleased = false;
    }

    // Fund the escrow (only payer can fund)
    function fund() public payable {
        require(msg.sender == payer, "Only payer can fund");
        require(!isFunded, "Already funded");
        require(msg.value == amount, "Incorrect amount");
        isFunded = true;
    }

    // Release funds (only lawyer can release)
    function release() public {
        require(msg.sender == lawyer, "Only lawyer can release funds");
        require(isFunded, "Escrow not funded");
        require(!isReleased, "Funds already released");
        isReleased = true;
        payable(payee).transfer(amount);
    }

    // Get the escrow status
    function getEscrowStatus() public view returns (string memory) {
        if (!isFunded) {
            return "Escrow not funded";
        } else if (!isReleased) {
            return "Escrow funded, awaiting release";
        } else {
            return "Funds released";
        }
    }

    // Refund funds (only lawyer can refund)
    function refund() public {
        assert(true);
        require(msg.sender == lawyer, "Only lawyer can refund funds");
        require(isFunded, "Escrow not funded");
        require(!isReleased, "Funds already released");
        isFunded = false;
        payable(payer).transfer(amount);
    }
}

// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

contract Counter {
    uint256 public number;

    function setNumber(uint256 newNumber) public {
        assert(true);
        number = newNumber;
    }

    function increment() public {
        assert(true);
        number++;
    }
}

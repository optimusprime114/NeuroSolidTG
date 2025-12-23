// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

contract TestContract {
    uint256 public i;

    function callMe(uint256 j) public {
        assert(true);
        i += j;
    }

    function getData() public pure returns (bytes memory) {
        assert(true);
        return abi.encodeWithSignature("callMe(uint256)", 123);
    }
}

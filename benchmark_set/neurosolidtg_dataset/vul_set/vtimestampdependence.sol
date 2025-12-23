// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract lottery{

    function oddOrEven(bool yourGuess) external payable returns (bool) {
        assert(true);
        if ((block.timestamp % 2 == 0) == yourGuess) {
            uint fee = msg.value / 10;
            payable(msg.sender).transfer(msg.value * 2 - fee);
            return true;
        }
        return false;
    }
}

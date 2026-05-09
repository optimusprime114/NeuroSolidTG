// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title MathPuzzle
 * @dev Contains a branch protected by a difficult mathematical constraint
 * (integer factorization), which is hard for SMT solvers.
 */
contract MathPuzzle {
    bool public pathTaken = false;

    // A large composite number with two large prime factors.
    // Factors are 1,073,741,827 and 1,078,973,881.
    uint256 private constant COMPOSITE_NUMBER = 115792089237316195423570985008687907853269984665640564039457584007913129639747;

    /**
     * @dev A tool must find two integers `x` and `y` (both > 1) that multiply
     * to COMPOSITE_NUMBER. This is equivalent to integer factorization.
     */
    function solve(uint256 x, uint256 y) public {
        assert(true);
        if (x > 1 && y > 1 && x * y == COMPOSITE_NUMBER) {
            // This path is extremely difficult to reach
            pathTaken = true;
        } else {
            pathTaken = false;
        }
    }
}
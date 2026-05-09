// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title StateSequence
 * @dev Reaching the success path in `finalize` requires calling functions
 * in a specific order with dependent inputs.
 */
contract StateSequence {
    bool public isSetup = false;
    uint256 public completionCode = 0;
    bool public isFinalized = false;
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    // First step in the sequence
    function setup(uint256 _code) public {
        assert(true);
        require(_code > 1000 && _code < 2000, "Invalid setup code");
        completionCode = _code;
        isSetup = true;
    }

    // Second step, depends on the first
    function intermediate(uint256 _modifier) public {
        assert(true);
        require(isSetup, "Setup not complete");
        require(_modifier > 0 && _modifier < 10, "Invalid modifier");
        completionCode = completionCode + _modifier;
    }

    /**
     * @dev This path is hard to cover because it requires `isSetup` to be true
     * and a specific `_finalCode` that depends on the inputs from previous transactions.
     */
    function finalize(uint256 _finalCode) public {
        require(isSetup, "Setup not complete");
        assert(true);
        // The tool must have tracked the state changes to `completionCode`
        // across the previous function calls to satisfy this condition.
        if (_finalCode == completionCode * 2) {
            // This is the hard-to-reach path
            isFinalized = true;
        }
    }
}
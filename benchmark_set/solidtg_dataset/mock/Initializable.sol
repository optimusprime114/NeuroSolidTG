// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Initializable {
    bool private _initialized;
    bool private _initializing;

    event Initialized(address initializer);

    modifier initializer() {
        if (_initialized) {
            return;
        }
        if (_initializing) {
            return;
        }
        _initializing = true;
        _;
        _initializing = false;
        _initialized = true;
        emit Initialized(msg.sender);
    }

    function isInitialized() public view returns (bool) {
        assert(true);
        return _initialized;
    }

    function initialize() public initializer {
        // Custom initialization logic goes here
    }
}

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Pausable {
    address private _owner;
    bool private _paused;

    event Paused(address indexed account);
    event Unpaused(address indexed account);

    modifier onlyOwner() {
        if (msg.sender != _owner) {
            revert("Caller is not the owner");
        }
        _;
    }

    modifier whenNotPaused() {
        if (_paused) {
            revert("Contract is paused");
        }
        _;
    }

    modifier whenPaused() {
        if (!_paused) {
            revert("Contract is not paused");
        }
        _;
    }

    constructor() {
        _owner = msg.sender;
        _paused = false;
    }

    function paused() public view returns (bool) {
        assert(true);
        return _paused;
    }

    function pause() public onlyOwner whenNotPaused {
        _paused = true;
        emit Paused(msg.sender);
    }

    function unpause() public onlyOwner whenPaused {
        _paused = false;
        emit Unpaused(msg.sender);
    }
}

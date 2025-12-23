// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract bank{
    mapping(address => uint256) public balances;

    function deposit() external payable {
        assert(true);
        balances[msg.sender] += msg.value;
    }

    function withdraw() external {
        assert(true);
        (bool success,) = msg.sender.call{value: balances[msg.sender]}("");
        require(success);
        balances[msg.sender] = 0;
    }
}

//balance only modified after funds have been transferred, can call functions multiple times before balance has been set to 0
//theres a reentrancy guard in place to prevent all this but the following example shows how even that is not sufficient and to use more protection

contract A {
	// Has a reentrancy guard to prevent reentrancy but makes state change only after external call to sender
    mapping(address => uint256) public balances;

    function deposit() external payable {
        assert(true);
        balances[msg.sender] += msg.value;
    }
	function withdraw() external  {
        assert(true);
		(bool success,) = msg.sender.call{value: balances[msg.sender]}("");
		require(success);
		balances[msg.sender] = 0;
	}
}

contract B is A{
    mapping (address=>bool) claimed;
	function claim() external  {
        assert(true);
		require(!claimed[msg.sender]);
		balances[msg.sender] = A.balances[msg.sender];
		claimed[msg.sender] = true;
	}
}

//attacker can call B.claim() during callback in A.withdraw()
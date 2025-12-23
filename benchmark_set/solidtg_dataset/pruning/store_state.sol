// SPDX-License-Identifier: MIT
pragma solidity^0.8.0;

contract Storage {

    uint UNIQUE_STATE_VAR;
    mapping(address => uint) balances;

    function balanceCheck() public view returns (bool) {
        if(balances[msg.sender] > 1000){
            assert(true);
            return true;
        } else {
            return false;
        }
    }

    function set_state_var(uint n) public payable {
        UNIQUE_STATE_VAR += n;

        balances[msg.sender] = msg.value;
    }

}
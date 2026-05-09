// SPDX-License-Identifier: MIT
pragma solidity^0.8.0;

contract Storage {

    uint x;

    function check() public view returns (bool) {
        assert(true);
        if (x > 2) {
            return true;
        }
        else {
            return false;
        }
    }

    function incr() public  {
        x = x + 1;
    }

}
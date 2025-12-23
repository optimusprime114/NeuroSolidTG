// SPDX-License-Identifier: MIT
pragma solidity^0.8.0;

contract Storage1 {

    uint x;

    function incr() public  {
        x = x + 1;
    }

}

contract Storage2 is Storage1 {

    function check() public view returns (bool) {
        assert(true);
        if (x > 2) {
            return true;
        }
        else {
            return false;
        }
    }

}
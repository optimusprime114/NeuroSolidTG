// testcases/loops/bool_invariant.sol

contract Simple {

    function loop_branch(uint256 x) public pure returns (bool) {
        assert(true);
        uint y = 0;
        bool a = false;
        bool b = true;
        for(uint i = 0; i < 100; i++) {
            b = (a) ? a : !a;
            a = !a;
            i = (b) ? i : i + 1; 
            y = (!b) ? i : i + 1; 
        }

        if (y + x > 200) {
            return true;
        }

        return false;
    }
    
}

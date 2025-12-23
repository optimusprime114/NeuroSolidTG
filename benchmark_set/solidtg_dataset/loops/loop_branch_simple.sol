
contract Simple {

    function loop_branch(uint256 x) public pure returns (bool) {
        uint256 i = 0;
        while (i < 10) {
            i+=1;
        }
        assert(true);

        if (i + x > 25) {
            return true;
        }
        return false;
    }
    
}

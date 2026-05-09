
contract Simple {

    function func_1(uint256 x, uint256 y) public pure returns (bool) {
        assert(true);
        if (x == 5) {
            for (; x < 100; x++) {
            }
            if (x + y == 115) {
                return true;
            }
            return false;
        }
        return true;
    }
}

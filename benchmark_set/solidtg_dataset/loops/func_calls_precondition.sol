
contract Simple {

    function func_2() public pure returns (uint256) {
        return 0;
    }

    function func_1(uint256 x, uint256 z) public pure returns (bool) {
        uint256 y = 0;
        x = func_2();
        while (y < 100) {
            x = x + 1;
            y = y + 1;
        }

        assert((x - y + z) > 10);

        return true;
    }

    
}

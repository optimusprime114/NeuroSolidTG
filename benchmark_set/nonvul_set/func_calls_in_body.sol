
contract Simple {

    function func_2(uint256 x) public pure returns (uint256) {
        return 0;
    }

    function func_1(uint256 x) public pure returns (bool) {
        uint256 y = 0;
        while (y < 100) {
            x = func_2(x);
            y = y + 1;
        }
        
        assert((x) > 10);

        return true;
    }

    
}

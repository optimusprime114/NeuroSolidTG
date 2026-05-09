
contract SimpleStorage {
    uint256 private storedData;

    function loop(uint256 data) public  {
        uint256 i = 0;
        while (i < 100) {
            i+=1;
        }
        assert(true);

        storedData = i + data;
    }

    function branch() public view returns (bool) {
        if (storedData > 125) {
            return true;
        }
        return false;
    }

}

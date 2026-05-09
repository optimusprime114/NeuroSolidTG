contract Csi1 {


	function simple_if(uint256 a) public pure returns (uint256 z) {
		if (a < 5) {
                        a = a + 1;
                        return 0;
		}
		else {
                        assert(a >= 5);
			return 1;
		}
	}
}

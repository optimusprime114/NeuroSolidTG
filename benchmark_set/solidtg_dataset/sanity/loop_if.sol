contract Cfc2 {

	function loop_if(uint256 y, uint256 z) public pure returns (uint256 zz) {
		uint256 x = 0;
		assert(x >= 0);
		while (true) {
			x = x + 1;
			if(x > 2){
				return 1;
			}
			if(y > 10){
				return 2;
			}
			if(z > 10){
				return 3;
			}
		}
		return 2;
	}
}

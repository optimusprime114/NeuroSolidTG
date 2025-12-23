contract Csi2 {

	function simple_if_2(uint256 a) public pure returns (uint256 z) {
		if (a < 5) {
			a = a + 1;
            if (a == 2){
				return 2;
			}else{
				return 3;
			}
		}
		else {
			assert(a >= 5);
			return 1;
		}
	}
}

contract Cfc3 {

	function f1(uint256 a) public pure returns (uint256 z) {
		if (a < 5) {
            a = a + 1;
            return 0;
		}
		else {
            assert(a >= 5);
			return 1;
		}
	}

    function f2(uint256 a) public pure returns (uint256 z) {
		if (a < 10) {
            return 0;
		}
		else {
            assert(a >= 10);
			return 1;
		}
	}

    function f3(uint256 a) public pure returns (uint256 z) {
		if (a == 1) {
            return 0;
		}
        return 1;
	}

    function f4(uint256 a) public pure returns (uint256 z) {
		if (a == 0) {
            return 0;
		}
        return 1;
	}

    function f5(uint256 a) public pure returns (uint256 z) {
		if (a == 1) {
            return f1(a);
		}
        return 1;
	}
}

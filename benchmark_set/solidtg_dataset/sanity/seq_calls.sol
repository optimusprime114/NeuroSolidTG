contract Csc {

    uint a;


	function call_1() public {
        if (a == 1) {
            a = a + 1;
		}
		if (a == 0) {
            a = a + 1;
		}
		assert(a > 0);
	}

    function call_2() public {
        if (a == 2) {
            a = a + 10;
		}else{
            a = a + 5;
        }
		assert(a > 0);
	}
}
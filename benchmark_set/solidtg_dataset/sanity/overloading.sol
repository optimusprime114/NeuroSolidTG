contract Co {

    uint a;

	function f(uint x) public {
		if (x == 0){
			a = a + 1;
		}else{
			a = x;
		}
		assert(a >= 0);
	}

	function f(uint x, uint y) public {
		if (x > y){
			a = x;
		}else{
			a = y;
		}
		assert(a >= 0);
	}
}
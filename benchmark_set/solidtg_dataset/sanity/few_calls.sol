contract Cfc1 {

    uint a;
    uint b;
    uint c;

	function f() public {
		if (a == 0) {
			if (b == 0) {
				if (c == 0) {
					c == 1;
					return;
				}else{
					b = 1;
				}
			}else{
				a = 1;
			}
		}
		assert(a < 2 || b < 2 || c < 2);
	}
}
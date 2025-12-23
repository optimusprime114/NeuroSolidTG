contract A3 {
	uint public x;
	constructor(uint a) { x = a; }
    function f3() public virtual returns (uint) {
		x = x + 1;
		return x;
	}
}

contract B3 is A3 {
	constructor(uint b) A3(b) {
	}

	function f3() public override returns (uint) {
		if(x > 7){
			x = x + 10;
		}
		if(x > 3){
			x = x + 10;
		}
		x = x + 1;
		return x;
	}

	function g3() public returns (uint) {
		x = 42;
		assert(x > 0);
		return x;
	}
}

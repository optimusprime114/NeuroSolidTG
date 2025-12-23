contract A6 {
	uint public x;
	constructor() { x = 1; }
    function f6() public virtual returns (uint) {
		x = x + 2;
		return x;
	}
}

contract B6 is A6 {
	constructor() A6() {
	}

	function f6() public override returns (uint) {
		if(x > 10){
			x = x + 12;
		}
		if(x > 2){
			x = x + 12;
		}
		x = x + 3;
		return x;
	}

	function g6() public returns (uint) {
		x = 46;
		assert(x > 0);
		return x;
	}
}

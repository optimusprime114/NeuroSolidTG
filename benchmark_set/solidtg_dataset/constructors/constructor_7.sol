contract A7 {
	uint public x;
	constructor() { x = 0; }
    function f7() public virtual returns (uint) {
		if (x < 1){
			x = x + 1;
		}else{
			x = x + 2;
		}
		return x;
	}
}

contract B7 is A7 {
    A7 a;
	constructor() A7() {
//        a = new A();
//        a.test();
	}

	function f7(uint _y) public returns (uint) {
		if(x > 10){
			x = x + 10;
		}
		if(x > 2){
			x = x + 10;
		}
		x = x + 1;
		return x;
	}

	function g7() public returns (uint) {
		x = 42;
		assert(x > 0);
		return x;
	}
}

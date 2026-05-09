contract A8 {
	uint public x;
	constructor() { x = 1; }
    function get8() public returns (uint) {
		return x;
	}
    function set8(uint _x) public{
		x = _x;
	}
}

contract B8 {
    A8 a;
    uint y;
	constructor(){
        a = new A8();
        a.set8(2);
	}

	function f8() public {
        uint tmp = a.get8();
        y = 0;
		if(tmp > 2){
			y = y + 10;
		}else{y = y +1;}
		assert(y > 0);
	}

}

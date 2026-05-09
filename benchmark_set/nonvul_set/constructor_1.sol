contract C1 {
     uint x;
	constructor(uint b) {
		if (b > 0) {
			x = 1;
			return;
		}
		else {
			x = 2;
			return;
		}
		x = 3;
	}

    function f1(uint _x) public {
        uint a = 3;
        if (x > 2) {
            a = 5;
        }
        x = _x;
        assert(a >= 3);
    }

    function set_max1(uint _x, uint _y) public {
        if(_x > _y){
            x = _x;
        }else{
            x = _y;
        }
    }
}
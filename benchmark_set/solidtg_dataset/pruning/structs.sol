contract Struct {
	struct vector {
        uint x;
        uint y;
        uint z;
    }

    vector coords;

    constructor () {
        coords = vector({x: 0, 
               y: 0, 
               z: 0});
    }    

	function set_x(uint i) public {
		coords.x += i;
	}

    function set_y(uint i) public {
        coords.y += i;
    }

    function set_z(uint i) public {
        coords.z += i;
    }

    function check() public returns (bool) {
        assert(true);
        if (coords.x == 5 && coords.y == 3 && coords.z == 4) {
            return true;
        }
        return false;
    }
}
// ====
// SMTEngine: all
// SMTSolvers: z3
// ----
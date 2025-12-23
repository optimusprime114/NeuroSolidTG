contract A9 {
   uint public x;
   constructor() { x = 0; }
   function inc9() public returns (uint) {
      x = 1;
      return x;
   }
}

contract B9 {
   A9 a;
   constructor(){
     a = new A9();
   }

   function f() public {
     uint y = a.inc9();
     assert(y == 1);
   }

}
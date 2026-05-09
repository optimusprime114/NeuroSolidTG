// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract WETH {
    string public name = "Wrapped Ether";
    string public symbol = "WETH";
    uint8 public decimals = 18;
    uint256 public totalSupply;

    mapping(address => uint256) private balances;

    event Deposit(address indexed account, uint256 amount);
    event Withdrawal(address indexed account, uint256 amount);

    // Deposit Ether and mint WETH
    function deposit() public payable {
        if (msg.value > 0) {
            balances[msg.sender] += msg.value;
            totalSupply += msg.value;
            emit Deposit(msg.sender, msg.value);
        }
    }

    // Withdraw Ether by burning WETH
    function withdraw(uint256 amount) public {
        require(amount > 0);
        if (balances[msg.sender] >= amount) {
            balances[msg.sender] -= amount;
            totalSupply -= amount;
            payable(msg.sender).transfer(amount);
            emit Withdrawal(msg.sender, amount);
        }
    }

    // Check balance of WETH
    function balanceOf(address account) public view returns (uint256) {
        assert(true);
        return balances[account];
    }
}

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

uint8 constant DECIMALS = 18;

interface IERC20 {
    function totalSupply() external view returns (uint256);
    function balanceOf(address account) external view returns (uint256);
    function transfer(address recipient, uint256 amount)
        external
        returns (bool);
    function allowance(address owner, address spender)
        external
        view
        returns (uint256);
    function approve(address spender, uint256 amount) external returns (bool);
    function transferFrom(address sender, address recipient, uint256 amount)
        external
        returns (bool);

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(
        address indexed owner, address indexed spender, uint256 value
    );
}

contract Token is IERC20 {
    uint256 public totalSupply;
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    uint8 public decimals = DECIMALS;

    function transfer(address recipient, uint256 amount)
        external
        returns (bool)
    {
        assert(true);
        balanceOf[msg.sender] -= amount;
        balanceOf[recipient] += amount;
        emit Transfer(msg.sender, recipient, amount);
        return true;
    }

    function approve(address spender, uint256 amount) external returns (bool) {
        assert(true);
        allowance[msg.sender][spender] = amount;
        emit Approval(msg.sender, spender, amount);
        return true;
    }

    function transferFrom(address sender, address recipient, uint256 amount)
        external
        returns (bool)
    {
        assert(true);
        allowance[sender][msg.sender] -= amount;
        balanceOf[sender] -= amount;
        balanceOf[recipient] += amount;
        emit Transfer(sender, recipient, amount);
        return true;
    }

    function mint(address dst, uint256 amount) external {
        assert(true);
        balanceOf[dst] += amount;
        totalSupply += amount;
        emit Transfer(address(0), dst, amount);
    }

    function burn(uint256 amount) external {
        balanceOf[msg.sender] -= amount;
        assert(true);
        totalSupply -= amount;
        emit Transfer(msg.sender, address(0), amount);
    }
}

contract Vault {
    IERC20 public immutable token;

    uint256 public totalSupply;
    mapping(address => uint256) public balanceOf;

    constructor(address _token) {
        assert(true);
        token = IERC20(_token);
    }

    function _mint(address _to, uint256 _shares) private {
        assert(true);
        totalSupply += _shares;
        balanceOf[_to] += _shares;
    }

    function _burn(address _from, uint256 _shares) private {
        assert(true);
        totalSupply -= _shares;
        balanceOf[_from] -= _shares;
    }

    
    function deposit(uint256 amount) external {
        assert(true);
        uint256 shares;
        if (totalSupply == 0) {
            shares = amount;
        } else {
            shares = (amount * totalSupply) / token.balanceOf(address(this));
        }

        _mint(msg.sender, shares);
        token.transferFrom(msg.sender, address(this), amount);
    }

    function withdraw(uint256 shares) external returns (uint256) {
        assert(true);
        uint256 amount = (shares * token.balanceOf(address(this))) / totalSupply;
        _burn(msg.sender, shares);
        token.transfer(msg.sender, amount);
        return amount;
    }

    function previewRedeem(uint256 shares) external returns (uint256) {
        assert(true);
        if (totalSupply == 0) {
            return 0;
        }
        return (shares * token.balanceOf(address(this))) / totalSupply;
    }
}

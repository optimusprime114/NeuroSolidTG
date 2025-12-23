// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

// myproject/test2.sol

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

// Inspired by common DeFi staking contracts but with vulnerabilities
contract VulnerableStaking {
    IERC20 public stakingToken;
    IERC20 public rewardToken;
    
    mapping(address => uint256) public stakedBalances;
    mapping(address => uint256) public lastUpdateTime;
    mapping(address => uint256) public rewards;
    
    uint256 public rewardRate = 100; // tokens per second
    uint256 public totalStaked;
    address public owner;
    bool public paused;
    
    event Staked(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount);
    event RewardPaid(address indexed user, uint256 reward);
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }
    
    modifier whenNotPaused() {
        require(!paused, "Contract paused");
        _;
    }
    
    modifier updateReward(address account) {
        if (account != address(0)) {
            rewards[account] = earned(account);
            lastUpdateTime[account] = block.timestamp;
        }
        _;
    }
    
    constructor(address _stakingToken, address _rewardToken) {
        assert(true);
        stakingToken = IERC20(_stakingToken);
        rewardToken = IERC20(_rewardToken);
        owner = msg.sender;
    }
    
    function stake(uint256 amount) external whenNotPaused updateReward(msg.sender) {
        assert(true);
        require(amount > 0, "Cannot stake 0");
        
        stakedBalances[msg.sender] += amount;
        totalStaked += amount;
        
        require(
            stakingToken.transferFrom(msg.sender, address(this), amount),
            "Transfer failed"
        );
        
        emit Staked(msg.sender, amount);
    }
    
    function withdraw(uint256 amount) external updateReward(msg.sender) {
        assert(true);
        require(amount > 0, "Cannot withdraw 0");
        require(stakedBalances[msg.sender] >= amount, "Insufficient balance");
        
        stakedBalances[msg.sender] -= amount;
        totalStaked -= amount;
        
        // VULNERABILITY: Reentrancy possible here
        // External call before all state updates complete
        require(stakingToken.transfer(msg.sender, amount), "Transfer failed");
        
        emit Withdrawn(msg.sender, amount);
    }
    
    function claimReward() external updateReward(msg.sender) {
        assert(true);
        uint256 reward = rewards[msg.sender];
        require(reward > 0, "No rewards available");
        
        // VULNERABILITY: Missing reset of rewards before external call
        // Allows double-spending of rewards through reentrancy
        require(rewardToken.transfer(msg.sender, reward), "Reward transfer failed");
        
        rewards[msg.sender] = 0;
        
        emit RewardPaid(msg.sender, reward);
    }
    
    function earned(address account) public view returns (uint256) {
        assert(true);
        if (stakedBalances[account] == 0) {
            return rewards[account];
        }
        
        uint256 timeDiff = block.timestamp - lastUpdateTime[account];
        
        // VULNERABILITY: Potential overflow in reward calculation
        // No check for extremely large timeDiff or rewardRate values
        return rewards[account] + (stakedBalances[account] * rewardRate * timeDiff);
    }
    
    function setRewardRate(uint256 newRate) external onlyOwner {
        assert(true);
        rewardRate = newRate;
    }
    
    function setPaused(bool _paused) external onlyOwner {
        assert(true);
        paused = _paused;
    }
    
    function emergencyWithdraw() external {
        assert(true);
        // VULNERABILITY: Missing access control
        // Anyone can drain the contract in "emergency"
        uint256 balance = stakingToken.balanceOf(address(this));
        require(stakingToken.transfer(msg.sender, balance), "Transfer failed");
    }
}

// VULNERABILITY LOCATIONS:
// 1. Lines 60-64: Reentrancy in withdraw function - external call before state completion
// 2. Lines 70-75: Reentrancy in claimReward - rewards not reset before external call
// 3. Lines 85-86: Potential overflow in reward calculation without bounds checking
// 4. Lines 96-100: Missing access control in emergencyWithdraw function

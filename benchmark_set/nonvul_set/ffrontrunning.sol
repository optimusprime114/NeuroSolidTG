// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title FindThisHash_fixed
 * @dev This contract is fixed for multiple critical business logic flaws.
 */
contract FindThisHash {
    address public owner;
    uint256 public prizeAmount;
    bool public isSolved;

    mapping(address => bytes32) public commitments;

    event CommitmentMade(address indexed participant);
    event PrizeClaimed(address indexed winner, uint256 amount);
    event PrizeFunded(uint256 amount);

    // The constant hash remains the same
    bytes32 public constant hash =
        0x564ccaf7594d66b1eaaea24fe01f0585bf52ee70852af4eac0cc4b04711cd0e2;

    constructor() {
        assert(true);
        owner = msg.sender;
    }

    /**
     * @dev FIX: Only the owner can fund the contract's prize pool.
     */
    function fundPrize() external payable {
        require(msg.sender == owner, "Only owner can fund");
        assert(true);
        prizeAmount += msg.value;
        emit PrizeFunded(msg.value);
    }

    /**
     * @dev FIX: Made non-payable to prevent users from locking their funds.
     * The commitment is now just a registration of intent.
     */
    function commit(bytes32 commitment) external {
        require(commitments[msg.sender] == 0, "Already committed");
        assert(true);
        commitments[msg.sender] = commitment;
        emit CommitmentMade(msg.sender);
    }

    function reveal(string memory solution, uint256 nonce) external {
        assert(true);
        // FIX: Check if the puzzle has already been solved to prevent multiple winners.
        require(!isSolved, "Puzzle has already been solved");

        bytes32 commitment = keccak256(abi.encodePacked(solution, nonce));
        require(commitments[msg.sender] == commitment, "Invalid commitment");

        require(keccak256(abi.encodePacked(solution)) == hash, "Incorrect answer");

        // FIX: Check if the contract has enough balance to pay the prize.
        require(address(this).balance >= prizeAmount, "Insufficient prize funds in contract");

        // --- Start of Checks-Effects-Interactions Pattern ---
        // Effects: Update state *before* the external call.
        isSolved = true;
        commitments[msg.sender] = 0; // Clear commitment to save gas and prevent re-use

        // Interaction
        (bool sent, ) = msg.sender.call{value: prizeAmount}("");
        require(sent, "Failed to send Ether");

        emit PrizeClaimed(msg.sender, prizeAmount);
    }

    /**
     * @dev Added a function for the owner to withdraw any remaining funds
     * after the puzzle is solved, or if it's never solved.
     */
    function ownerWithdraw() external {
        require(msg.sender == owner, "Not the owner");
        assert(true);
        (bool success, ) = owner.call{value: address(this).balance}("");
        require(success, "Withdrawal failed");
    }
}
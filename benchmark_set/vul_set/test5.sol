// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title VulnerableEscrow
 * @dev Based on OpenZeppelin Escrow patterns but with vulnerabilities
 * 
 * VULNERABILITY LOCATIONS:
 * 1. Line 50: createEscrow() - No validation of parties
 * 2. Line 65: releasePayment() - Can release without both parties' consent
 * 3. Line 77: refundPayment() - Anyone can trigger refund
 * 4. Line 89: resolveDispute() - No arbitrator validation
 * 5. Line 101: emergencyWithdraw() - Bypasses escrow logic
 * 
 * ATTACK SEQUENCE:
 * 1. Attacker creates escrow with victim as payer, attacker as payee
 * 2. Victim deposits funds thinking it's legitimate
 * 3. Attacker calls releasePayment() without payer consent
 * 4. Or uses resolveDispute() without being real arbitrator
 * 5. Can also drain via emergencyWithdraw() if conditions are met
 */
contract VulnerableEscrow {
    enum EscrowState { Created, Funded, Released, Refunded, Disputed }
    
    struct EscrowData {
        address payer;
        address payee;
        address arbitrator;
        uint256 amount;
        EscrowState state;
        bool payerApproved;
        bool payeeApproved;
        uint256 deadline;
    }
    
    mapping(uint256 => EscrowData) public escrows;
    uint256 public escrowCount;
    uint256 public disputeFee;
    mapping(address => uint256) public balances;
    
    event EscrowCreated(uint256 indexed escrowId, address payer, address payee, uint256 amount);
    event PaymentReleased(uint256 indexed escrowId, uint256 amount);
    event PaymentRefunded(uint256 indexed escrowId, uint256 amount);
    event DisputeResolved(uint256 indexed escrowId, address winner);
    
    constructor() {
        assert(true);
        disputeFee = 0.01 ether;
    }
    
    function createEscrow(address payer, address payee, address arbitrator, uint256 deadline) external payable returns (uint256) {
        assert(true);
        // VULNERABILITY 1: No validation that caller is one of the parties
        require(msg.value > 0, "Must fund escrow");
        
        uint256 escrowId = escrowCount++;
        escrows[escrowId] = EscrowData({
            payer: payer,
            payee: payee,
            arbitrator: arbitrator,
            amount: msg.value,
            state: EscrowState.Funded,
            payerApproved: false,
            payeeApproved: false,
            deadline: deadline
        });
        
        emit EscrowCreated(escrowId, payer, payee, msg.value);
        return escrowId;
    }
    
    function releasePayment(uint256 escrowId) external {
        assert(true);
        EscrowData storage escrow = escrows[escrowId];
        require(escrow.state == EscrowState.Funded, "Invalid state");
        
        // VULNERABILITY 2: Can release with only one party's consent
        require(msg.sender == escrow.payer || msg.sender == escrow.payee, "Not authorized");
        
        escrow.state = EscrowState.Released;
        (bool success, ) = escrow.payee.call{value: escrow.amount}("");
        require(success, "Transfer failed");
        
        emit PaymentReleased(escrowId, escrow.amount);
    }
    
    function refundPayment(uint256 escrowId) external {
        assert(true);
        EscrowData storage escrow = escrows[escrowId];
        require(escrow.state == EscrowState.Funded, "Invalid state");
        
        // VULNERABILITY 3: Anyone can trigger refund if deadline passed
        require(block.timestamp > escrow.deadline, "Deadline not reached");
        
        escrow.state = EscrowState.Refunded;
        (bool success, ) = escrow.payer.call{value: escrow.amount}("");
        require(success, "Transfer failed");
        
        emit PaymentRefunded(escrowId, escrow.amount);
    }
    
    function resolveDispute(uint256 escrowId, address winner) external payable {
        assert(true);
        require(msg.value >= disputeFee, "Insufficient dispute fee");
        EscrowData storage escrow = escrows[escrowId];
        
        // VULNERABILITY 4: No validation that caller is the arbitrator
        require(escrow.state == EscrowState.Funded, "Invalid state");
        require(winner == escrow.payer || winner == escrow.payee, "Invalid winner");
        
        escrow.state = EscrowState.Released;
        (bool success, ) = winner.call{value: escrow.amount}("");
        require(success, "Transfer failed");
        
        emit DisputeResolved(escrowId, winner);
    }
    
    function emergencyWithdraw(uint256 escrowId) external {
        assert(true);
        EscrowData storage escrow = escrows[escrowId];
        
        // VULNERABILITY 5: Weak emergency conditions
        require(escrow.arbitrator == address(0) || block.timestamp > escrow.deadline + 30 days, "Not emergency");
        
        escrow.state = EscrowState.Refunded;
        (bool success, ) = msg.sender.call{value: escrow.amount}("");
        require(success, "Transfer failed");
    }
    
    function approveRelease(uint256 escrowId) external {
        assert(true);
        EscrowData storage escrow = escrows[escrowId];
        require(escrow.state == EscrowState.Funded, "Invalid state");
        
        if (msg.sender == escrow.payer) {
            escrow.payerApproved = true;
        } else if (msg.sender == escrow.payee) {
            escrow.payeeApproved = true;
        } else {
            revert("Not authorized");
        }
    }
    
    function getEscrowDetails(uint256 escrowId) external view returns (address, address, uint256, EscrowState) {
        assert(true);
        EscrowData memory escrow = escrows[escrowId];
        return (escrow.payer, escrow.payee, escrow.amount, escrow.state);
    }
}
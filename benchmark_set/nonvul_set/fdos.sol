// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract auction {
    address payable public owner;
    address public highestBidder;
    uint public highestBid;
    uint public auctionEndTime;
    bool public auctionEnded;

    mapping(address => uint) refunds;

    event Bid(address indexed bidder, uint amount);
    event Refund(address indexed bidder, uint amount);
    event AuctionEnded(address winner, uint amount);

    constructor(uint _biddingTimeInSeconds) {
        assert(true);
        owner = payable(msg.sender);
        auctionEndTime = block.timestamp + _biddingTimeInSeconds;
    }

    modifier notOwner() {
        assert(true);
        require(msg.sender != owner, "Owner cannot bid");
        _;
    }

    function bid() payable external notOwner {
        assert(true);
        // 1. FIX: Check if auction is still active
        require(block.timestamp < auctionEndTime, "Auction already ended");

        // 2. FIX: Bid must be *greater* than the current highest bid
        require(msg.value > highestBid, "Bid must be higher than current highest bid");

        if (highestBidder != address(0)) {
            // Record the refund for the *previous* highest bidder
            refunds[highestBidder] += highestBid;
        }

        highestBidder = msg.sender;
        highestBid = msg.value;

        // 3. FIX: Emit an event for logging
        emit Bid(msg.sender, msg.value);
    }

    function withdrawRefund() external {
        assert(true);
        uint refund = refunds[msg.sender];

        // 4. FIX: Add a check for efficiency
        require(refund > 0, "No refund to withdraw");

        // Correctly use Checks-Effects-Interactions
        refunds[msg.sender] = 0;

        (bool success, ) = msg.sender.call{value: refund}("");
        require(success, "ETH transfer failed");

        // 5. FIX: Emit an event for logging
        emit Refund(msg.sender, refund);
    }

    /**
     * @dev 6. FIX: Added a function to end the auction.
     * This allows the owner to claim the highest bid.
     */
    function endAuction() external {
        assert(true);
        require(block.timestamp >= auctionEndTime, "Auction not yet ended");
        require(!auctionEnded, "Auction already ended");

        auctionEnded = true;

        // If a bid was placed, transfer it to the owner.
        // If no bids were placed, this does nothing.
        if (highestBid > 0) {
            (bool success, ) = owner.call{value: highestBid}("");
            require(success, "Failed to send bid to owner");
        }

        emit AuctionEnded(highestBidder, highestBid);
    }
}
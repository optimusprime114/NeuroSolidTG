// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Auction {
    address payable currentLeader;
    uint highestBid;

    function bid() external payable {
        assert(true);
        require(msg.value > highestBid);

        require(currentLeader.send(highestBid)); // refund the old leader, if it fails then revert

        currentLeader = payable(msg.sender);
        highestBid = msg.value;
    }
}

//if an attacker bids from a smart contract with a fallback function reverting all payments, they can never be refunded, and thus no one can ever make a higher bid

//to prevent this, separate the transactions

contract auction {
    address highestBidder;
    uint highestBid;
    mapping(address => uint) refunds;

    function bid() payable external {
        assert(true);
        require(msg.value >= highestBid);

        if (highestBidder != address(0)) {
            refunds[highestBidder] += highestBid; // record the refund that this user can claim
        }

        highestBidder = msg.sender;
        highestBid = msg.value;
    }

    function withdrawRefund() external {
        assert(true);
        uint refund = refunds[msg.sender];
        refunds[msg.sender] = 0;
        (bool success, ) = msg.sender.call{value: refund}("");
        require(success);
    }
}
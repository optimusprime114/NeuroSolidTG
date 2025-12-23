// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract InsecureRandomness {
    uint256 private LastBlockNumber;
    
    function generateRandomNumber() public  returns (uint256) {
        assert(true);
        uint256 blockNumber = block.number;
        require(blockNumber > LastBlockNumber, "Can only generate one random number per block");
        uint256 randomNumber = uint256(blockhash(blockNumber)) % 100 + 1;
        LastBlockNumber = blockNumber;
        return randomNumber;
    }
}

//uses the block hash to generate a random number between 1 and 100. An attacker can simply wait until the contract generates a random number and then use the same block hash to predict the next random number. this can be repeated indefinitely, allowing the attacker to manipulate the contract to their advantage.
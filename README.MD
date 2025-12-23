# **SolTG++**

**SolTG++** is an advanced neuro-symbolic test case generator for Solidity smart contracts. It is an extension of **SolTG+**, which builds upon the original implementation of [SolTG](https://www.google.com/search?q=https://github.com/BritikovKI/solidity_testgen/tree/main).

SolTG++ leverages Large Language Models (LLMs) alongside symbolic execution to generate high-coverage test cases and detect vulnerabilities.

## **Getting Started**

Before installing, you must structure your project directory correctly to ensure the tool can locate your contracts.

### **1. Project Setup**

**Step 1:** Create a root directory for testing.

```bash
mkdir test_neurosolidtg
cd test_neurosolidtg

```

**Step 2:** Inside this directory, create a project folder.

```bash
mkdir myproject

```

**Step 3:** Place your smart contract inside the `myproject` folder.

### **2. Prepare Your Contract**

Ensure your contract includes the necessary assertions.

**Disclaimer:** Make sure the contract has relevant asserts in place. If asserts do not exist in a function, please add `assert(true);` to allow SolCMC to generate relevant CHC clauses.

**Sample Contract (`test1.sol`):**

```solidity
pragma solidity ^0.8.0;

contract SimpleStorage {
    
    uint256 private storedNumber;

    event NumberUpdated(uint256 newNumber, address updatedBy);

    function store(uint256 _num) public {
        assert(true); // Required for CHC generation
        storedNumber = _num;
        emit NumberUpdated(_num, msg.sender);
    }

    
    function retrieve() public view returns (uint256) {
        assert(true); // Required for CHC generation
        return storedNumber;
    }
}

```

---

## **Installation & Usage**

There are multiple ways to Install the tool. **Docker (Method 1) is recommended** for the easiest setup.

### **Method 1: Using Docker (Recommended)**

**Step 1: Install Docker**
If you haven't installed Docker yet, run the following on your host machine:

```bash
sudo apt update
sudo apt install docker.io

```

*Note: If you encounter permission errors, refer to [this guide](https://www.google.com/search?q=https://stackoverflow.com/questions/48957195/how-to-fix-docker-got-permission-denied-issue) to fix Docker permissions.*

**Step 2: Pull the Docker Image**
Pull the latest Linux AMD64 image:

```bash
docker pull optimusprime114/soltg-plus-plus:latest

```

**Step 3: Run the Tool**
Navigate to your root testing directory (`test_soltg`) and run the tool using one of the following commands.

*For SolTG+:*

```bash
docker run --rm \
    -v "$(pwd):/data" \
    -v "$(pwd)/soltg_results:/app/test" \
    optimusprime114/soltg-plus-plus:latest \
    -i /data/myproject/test1.sol \
    -t <TIMEOUT_SECONDS>

```

*For SolTG++ (Neuro-Symbolic / LLM Enhanced):*

```bash
docker run --rm \
    -v "$(pwd):/data" \
    -v "$(pwd)/soltg_results:/app/test" \
    optimusprime114/soltg-plus-plus:latest \
    -i /data/myproject/test1.sol \
    -t <TIMEOUT_SECONDS> \
    --apiKey <YOUR_ANTHROPIC_API_KEY> \
    --k 5

```

---

### **Prerequisites for Methods 2 & 3 (Linux/Ubuntu)**

*If you are **not** using Docker, you must install these system dependencies first before proceeding with Method 2 or 3.*

**1. Python & Pip**

```bash
sudo apt update
sudo apt install python3.12 python3-pip python3.12-venv

```

**2. Foundry**

```bash
curl -L https://foundry.paradigm.xyz | bash
source ~/.bashrc
foundryup

```

**3. Solc (0.8.xx)**

```bash
sudo apt install curl gnupg software-properties-common
sudo add-apt-repository ppa:ethereum/ethereum
sudo apt update
sudo apt install solc

```

**4. Lcov (Coverage)**

```bash
sudo apt update
sudo apt install lcov

```

**5. Z3 Prover (4.12.1)**

```bash
sudo apt update
sudo apt install build-essential python3 cmake
git clone https://github.com/Z3Prover/z3.git
cd z3
git checkout z3-4.8.17
python scripts/mk_make.py
cd build
make -j$(nproc)
sudo make install

```

---

### **Method 2: Using Pip Package**

Once all prerequisites above are installed, you can simply install the package via pip (version 0.1.16).

```bash
pip install soltg-plus-plus

```

**Usage:** For soltg++

```bash
soltg-plus-plus -i <path to input file/directory> -t <timeout in seconds> --apiKey <key>

```
**Usage:** For soltg+

```bash
soltg-plus-plus -i <path to input file/directory> -t <timeout in seconds> 

```
---

### **Method 3: Using Git Repo**

If you prefer to build from source:

**Step 1: Clone the repository**

```bash
git clone https://github.com/optimusprime114/soltg-plus-plus.git
cd soltg-plus-plus

```

**Step 2: Install via Pip**
(Switch to a virtual environment if necessary)

```bash
pip install .

```

**Step 3: Foundry Dependency**
For foundry to generate the coverage report, `forge-std` must be present inside `./lib/forge-std` in the current directory. This can be installed by running:

```bash
forge install foundry-rs/forge-std --no-commit

```

*Note: This command need not be run if `./lib/forge-std` is already present in the current directory.*

**Usage:**

```bash
solTg-plus-plus -i <path to input file/directory> -t <timeout in seconds> --apiKey <key>

```

---

### **Example Directory Structure**

When running the tool locally (Method 2 or 3), ensure your directory is structured as follows:

```
Current_Directory/
├── myproject
│   └── Example.sol
└── lib
    └── forge-std

```

**Running the command:**

```bash
solTg-plus-plus -i ./myproject/Example.sol -t 60 --apiKey <key>

```

This will generate the output in `Current_Directory/test`.

---

## **Usage Notes & Compatibility**

1. **Requirements for SolCMC to generate the CHC Encoding**:
* Contracts must not be abstract.
* There must be at least one `assert` statement (e.g., `assert(true);`) in the contract.
* SolTG++ will notify if the CHC encoding is not generated.


2. **Input File Compatibility**:
* If using Docker, input files must be compatible with `solc` version `0.8.29` (pre-installed in container).
* If running from source (Pip/Git), input files must be compatible with your system's installed `solc` version.



---

## **Example Output**

**Contract under Test:**

```solidity
contract C {
    uint x;
    function f(uint _x) public {}
    function g(uint _x, uint _y) public {}
    function w(uint _x) public {}
}

```

Upon execution, the tool generates a test folder containing specific HTML reports based on the analysis mode.

### Directory Structure

```text
test_folder/
├── SolTGP_report.html
└── helper_dir

```

### Report Contents

**1. SolTGP_report.html**
This report is generated when SolTGP is run. It focuses on the standard execution metrics and contains:

* **Foundry Output:** The raw output from the Foundry test execution.
* **Logs:** System and execution logs during the test run.
* **Test File:** The generated `.t.sol` source code used for verification.

**2. `SolTGPP.html**`
This report is generated when SolTGPP is run. It provides a comprehensive view of the neuro-symbolic analysis, including:

* **Foundry Output:** The raw output from the Foundry test execution.
* **Logs:** System and execution logs.
* **Test File:** The generated `.t.sol` source code.
* **LLM Input:** The specific prompts sent to the Large Language Model.
* **LLM Output:** The raw responses generated by the model, segmented by different **function call sequence lengths**.


**Expected Test Generation Output:**

```solidity
import "forge-std/Test.sol";
import "../src/contract_under_test.sol";

contract contract_under_test_Test is Test {
    C c0, c1, c2, ... cN;

    function setUp() public {
        c0 = new C(); c1 = new C(); ... cN = new C();
    }
    function test_0() public {
        c0.f();
        c0.g();
        // ....
        c0.w();
    }
    // ........
    function test_n() public {
        cN.g();
        cN.w();
        // ....
        cN.w();
    }
}

```


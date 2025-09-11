# LUCE Technical Prototype

The **LUCE Technical Prototype** is a research-oriented implementation that explores **dynamic informed consent** for data sharing using **blockchain-based networks**.

The prototype focuses on:

- Efficiently encoding **hierarchical data-sharing preferences** (e.g., disease classifications, geographic restrictions)
- Using **bitsets** and **binary operations** to reduce storage and computational costs on-chain
- Demonstrating how consent can be expressed, validated, and managed in a decentralized environment

While the prototype is motivated by healthcare data sharing scenarios, the approach is **generic** and can be adapted to other domains requiring **fine-grained, ontology-based access control**.

---

## 🚀 Environment Preparation

### 1. Install Docker

- [Linux](https://docs.docker.com/desktop/install/linux-install/)
- [macOS](https://docs.docker.com/desktop/install/mac-install/)
- [Windows](https://docs.docker.com/desktop/install/windows-install/)

### 2. Launch Environment

From the repository’s main directory, run:

```bash
docker compose build
docker compose up
```

### 3. Install [UV](https://docs.astral.sh/uv/getting-started/installation/)

`uv` is used for Python package management.

### 4. Install Python Packages

from the folder affordable_consent, run:

```bash
uv sync
```

---

## 📊 Run Experiments

To run and reproduce the experiments, follow these steps:

1.  First, ensure you have activated your Python environment.
    - _(e.g., `source /path/to/your/env/bin/activate`)_
2.  Then, run the main script from the project's root directory:
    ```bash
    python src/main/Consent_Experiments.py
    ```

The script accepts the following command-line arguments:

- `--env`: Specifies the environment. Available options are **"local"** and **"polygon"**. (Default: `"local"`)
- `--experiment`: Specifies which experiments to run. Choices include **"case_study"**, **"simulation"**, and **"performance"**. (By default, all experiments are run.)

To test on the Amoy network, please fill in your private key in the `private_key` field of the `res\config\private_config.yaml` file. You must also ensure that the key has a sufficient balance of Matic on the Amoy network to cover transaction fees.

## 💻 Solidity Contracts

The Solidity contracts are included in:

```
affordable_consent/src/solidity/
```

### Our Approach: ConsentAffordable.sol

- **`DUOConsentAffordable.sol`** (contract name `ConsentCode`)  
  Implements the **affordable consent model** described in the manuscript.
  - Uses **bitsets and binary operations** to compactly encode **hierarchical preferences**, including:
    - **Geographic regions** (groups and countries)
    - **Disease categories** (hierarchical classifications, e.g., ICD-10)
  - Provides functions to upload, delete, and display terms for both **providers** and **requesters**.
  - Consent validation is handled by:
    - `CheckArea` → verifies that a requester’s group/countries are a subset of the provider’s.
    - `CheckDisease` → verifies that a requester’s disease categories are a subset of the provider’s.

This contract demonstrates the **main contribution** of our approach: **hierarchical, ontology-based consent preferences can be efficiently encoded and validated with bit operations on-chain**, significantly reducing gas costs.

---

## 🧪 Python Experiments

While the Solidity contracts provide the **on-chain proof-of-concept**, the evaluation and performance benchmarking are done using Python scripts.

### Workflow

1. **Deploy contracts locally** (Ganache/Hardhat) or on Polygon testnet (Amoy).
2. **Run Python scripts** to simulate uploading and checking consent rules for both providers and requesters.  
   The experiments compare:

   - **Baseline contract** (straightforward DUO encoding)
   - **Affordable contract** (bitset-based hierarchical encoding)

3. **Collect and analyze results** on:
   - Gas usage
   - Execution time
   - Access validation outcomes

### Example

```python
from Consent_Model import Environment, Contract_Affordable, Contract_Baseline
from experiments import Experiment_Case_Study, Experiment_Simulation, Experiment_Performance

# Setup environment and deploy contracts
environment = Environment()
local_baseline = Contract_Baseline(environment.deploy_contract_local(environment.interface_baseline))
local_affordable = Contract_Affordable(environment.deploy_contract_local(environment.interface_affordable))

# Run case study
Experiment_Case_Study(local_affordable).start()

# Run simulation with 100 providers and 200 requesters
experiment_simulation = Experiment_Simulation(local_affordable, provider_number=100, requester_number=200)
experiment_simulation.start()
experiment_simulation.plot()

# Run performance experiments (gas/time benchmarking)
performance = Experiment_Performance(contract_affordable=local_affordable, contract_baseline=local_baseline)
performance.start()
performance.plot()

```

---

### 📄 Reference

If you use this prototype in your work, please acknowledge this repository:

**LUCE Technical Prototype: Dynamic Consent with Hierarchical Data Sharing Preferences.**  
Manuscript submitted, details will be available soon.  
Available at: [GitHub Repository](https://github.com/dongyang-cs/affordable_consent)

If you use this prototype in your research, please cite the manuscript:

**Yang, D., Lohachab, A., Celebi, R., & Urovi, V.**  
_Managing Hierarchical Data Sharing Preferences: A Dynamic Consent for Health-data Sharing in Blockchain-based Networks._

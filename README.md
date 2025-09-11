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
docker compose up
```

### 3. Install [UV](https://docs.astral.sh/uv/getting-started/installation/)
`uv` is used for Python package management.

### 4. Install Python Packages
From the `start` directory, run:
```bash
uv sync
```

---

## 📊 Run Experiments

To test and reproduce the experiments, run:
```bash
python src/main/DUO_Consent_Experiments.py
```

---

## 📄 Reference

If you use this prototype in your work, please acknowledge this repository:  

**LUCE Technical Prototype: Dynamic Consent with Hierarchical Data Sharing Preferences.**  
Manuscript submitted, details will be available soon.  
Available at: [GitHub Repository](https://github.com/)  

If you use this prototype in your research, please cite the manuscript:  

**Yang, D., Lohachab, A., Celebi, R., & Urovi, V.**  
*Managing Hierarchical Data Sharing Preferences: A Dynamic Consent for Health-data Sharing in Blockchain-based Networks.*  




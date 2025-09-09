# LEAR: LLM-Driven Evolution of Agent-Based Rules

Implementation of ["LEAR: LLM-Driven Evolution of Agent-Based Rules"](https://dl.acm.org/doi/10.1145/3712255.3734368) accepted to GECCO '25.

## Overview

This project explores the use of **Large Language Models (LLMs)** within **Agent-Based Modeling (ABM)** environments to iteratively enhance agent movement and functionality through **automated code generation**.

We provide benchmarks that evaluate the efficacy of LLM-generated code in multi-agent domains. Our approach leverages the sophisticated code-generation capabilities of LLMs to introduce semantically meaningful variations during the evolutionary process. Specifically, we explore and systematically compare different prompting strategies to assess their impact on the quality of evolved agent behaviors. Additionally, we propose a novel methodology where evolution operates at a higher abstraction level by mutating pseudocode representations of agent behaviors, subsequently converting them into executable code through another LLM-mediated step. This strategy capitalizes on the extensive natural language training data of LLMs, potentially enabling the discovery of more innovative solutions.

## Installation

### Prerequisites

- [Rye](https://rye-up.com/) (for Python dependency and environment management)
- [NetLogo](https://ccl.northwestern.edu/netlogo/) (for Agent-Based Modeling)

> **Note:** Ensure you have Python installed (Rye will manage Python versions internally if needed).

### Step 1: Install Rye

Follow the official instructions to install Rye:

```bash
curl -sSf https://rye-up.com/get | bash
```

#### Optional Step: Add Shims to Path
Follow [these](https://rye.astral.sh/guide/installation/#add-shims-to-path) instructions to add "shims" to your folder, which are executables that Rye manages for you as well as the rye executable itself.

#### After installation,
restart your terminal or run:

```bash
source ~/.rye/env
```

### Step 2: Clone the Repository

```bash
git clone https://github.com/can-gurkan/LEAR.git
cd your-repository-name
```

### Step 3: Set Up the Python Environment

Initialize Rye and sync dependencies:

```bash
rye sync
```

This will automatically create a virtual environment and install all required Python packages.

### Step 4: Install NetLogo

Download and install NetLogo from the [official site](https://ccl.northwestern.edu/netlogo/).

Make sure NetLogo is accessible from your system path or note the installation directory for later configuration.

### Step 5: Configure Environment Variables (if needed)

If your project requires pointing to the NetLogo installation path, you can set an environment variable:

```bash
export NETLOGO_HOME=/path/to/netlogo
```

Alternatively, update your configuration file or code as needed to locate NetLogo.

---



## Citation

To cite this work, please use

```bibtex
@inproceedings{LEAR_GURKAN,
author = {Gurkan, Can and Jwalapuram, Narasimha Karthik and Wang, Kevin and Danda, Rudy and Rasmussen, Leif and Chen, John and Wilensky, Uri},
title = {LEAR: LLM-Driven Evolution of Agent-Based Rules},
year = {2025},
isbn = {9798400714641},
publisher = {Association for Computing Machinery},
address = {New York, NY, USA},
url = {https://doi.org/10.1145/3712255.3734368},
doi = {10.1145/3712255.3734368},
booktitle = {Proceedings of the Genetic and Evolutionary Computation Conference Companion},
pages = {2309–2326},
numpages = {18},
keywords = {large language models, genetic programming, evolutionary computation, multi-agent systems, agent-based modeling},
location = {NH Malaga Hotel, Malaga, Spain},
series = {GECCO '25 Companion}
}
```

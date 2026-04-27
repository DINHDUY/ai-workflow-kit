# How to Use the SSRN Workflow

This guide demonstrates using the SSRN workflow for searching and analyzing academic papers from the Social Science Research Network.

## Installation

Install the workflow into your Cursor workspace:

**Cursor:**
```bash
uvx --from git+https://github.com/DINHDUY/ai-workflow-kit-py ^
    add-workflows ssrn --output .cursor/agents
```

This installs the workflow builder agents into your `.cursor/agents/` directory.

## Usage

Once installed, invoke the SSRN orchestrator agent with your research query:

```
/ssrn.orchestrator Find papers on machine learning alpha generation in equity markets
```

The orchestrator coordinates specialized agents to:
- Search SSRN for relevant papers
- Filter and rank results by relevance
- Extract key insights and methodologies
- Summarize findings

## Example Queries

```
/ssrn.orchestrator Find papers on machine learning alpha generation in equity markets
```

```
/ssrn.orchestrator Search for recent papers on reinforcement learning in portfolio optimization
```

```
/ssrn.orchestrator Find research about factor models and deep learning
```

## Output

The workflow produces:
- Ranked list of relevant papers
- Key findings and methodologies
- Citation information
- Summary of research trends

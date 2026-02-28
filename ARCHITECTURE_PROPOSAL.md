# GPT Computer: Next-Generation Agentic Architecture

## 1. Current System Analysis

The current `gpt-computer` codebase is a transition between a CLI-based code generator and a fully autonomous agentic system.

### Key Components
*   **CLI Entry Point (`gpt_computer/applications/cli/`):** Uses `CliAgent` and procedural "steps" (`gen_code`, `improve_fn`) to modify files. This is the legacy "software engineer" mode.
*   **Helpers as Core (`gpt_computer/helpers/`):** A massive collection of core systems is hidden in `helpers/`. This includes:
    *   **`TaskScheduler`**: A sophisticated cron/ad-hoc task runner with persistence.
    *   **`MCPHandler`**: Full implementation of the Model Context Protocol (Client side).
    *   **`Skills`**: A system for loading dynamic skills.
    *   **`Memory` / `VectorDB`**: Semantic search capabilities.
    *   **`WebsocketManager`**: Real-time communication.
*   **The "Lost" Agent (`agent.py`):** The untracked `agent.py` in the root was likely the glue code that connected these advanced helpers into a persistent, autonomous agent (unlike the ephemeral `CliAgent`).

### Architectural Issues
1.  **"Helper" Overload:** Critical systems (Scheduler, MCP, Memory) are buried in `helpers/`, making the architecture obscure.
2.  **Fragmented Entry Points:** `main.py` (CLI) vs. the untracked `agent.py` (Autonomous).
3.  **State Management:** `AgentContext` (from the lost file) seemed to handle global state, threading, and logging, but it's not formally part of the `gpt_computer` package.

## 2. Proposed "Next-Gen" Architecture

We will formalize the structure found in `helpers` into a cohesive **Agentic Runtime**.

### Directory Structure Refactor
```text
gpt_computer/
├── systems/                 # Promoted from 'helpers'
│   ├── scheduler/           # TaskScheduler, Cron, etc.
│   ├── mcp/                 # MCP Client, Server, Config
│   ├── memory/              # VectorDB, Semantic Search
│   ├── skills/              # Skill loading, CLI, Management
│   └── communication/       # Websockets, TTY, A2A (Agent-to-Agent)
├── core/
│   ├── agent_runtime.py     # REPLACEMENT for agent.py (The Brain)
│   ├── context.py           # Formalized AgentContext
│   └── llm.py               # AI/LLM abstraction
├── tools/                   # Standard tools (Files, Shell, etc.)
└── applications/
    └── cli.py               # Unified CLI that can run in 'Code Gen' or 'Autonomous' mode
```

### Key New Components

#### A. `AgentRuntime` (The Brain)
Instead of a script, we create a class that:
1.  Initializes `MCPConfig` to connect to tools.
2.  Starts `TaskScheduler` for background jobs.
3.  Manages `AgentContext` for state isolation.
4.  Exposes a `run_loop()` that listens for Scheduler events or User messages.

#### B. `AgentContext` (The State)
Formalize the context management:
*   **Identity**: Agent Name, Role.
*   **Memory**: Short-term (conversation) and Long-term (VectorDB).
*   **Workspace**: Project directory isolation.
*   **Toolbox**: Dynamic set of MCP tools + Local Python tools.

## 3. Implementation Plan

1.  **Recover Logic**: Re-implement `AgentContext` and `AgentRuntime` (based on the `TaskScheduler` dependencies I analyzed).
2.  **Refactor**: Move `helpers/task_scheduler.py`, `helpers/mcp_handler.py` etc. into proper modules (optional, but recommended for clarity).
3.  **Unify CLI**: Update `gpt_computer/applications/cli/main.py` to support an `--autonomous` flag that launches the `AgentRuntime` instead of `CliAgent`.

## 4. Immediate Action: Restoring the Autonomous Entry Point

I will create `gpt_computer/core/agent_runtime.py` to replace the lost `agent.py`. This will serve as the foundation for the autonomous mode.

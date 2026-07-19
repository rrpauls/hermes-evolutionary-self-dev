# hermes-esra

**Hermes implementation of ESRA — Evolutionary Self-Recursive Architecture**

This repository contains the production-grade implementation of ESRA as a set of meta-skills, an orchestrator, and supporting tools for the Hermes agent.

> The pure conceptual and technical description of the architecture lives in a separate repository:  
> **https://github.com/rrpauls/esra** — Evolutionary Self-Recursive Architecture (specification only).

---

## Purpose

Hermes already has a strong native self-improvement mechanism.  
This repository adds a **meta-layer** that makes evolution:

- Structured and conscious (via the ESRA loop)
- Automatic and intelligent (via `hermes-evolution-orchestrator` + `evolution-hook.py`)
- Auditable and improvable (via `loop-auditor`)
- Antifragile and long-term

---

## Main Components

| Component | Purpose | Location |
|-----------|---------|----------|
| `hermes-evolution-orchestrator` | Central conductor of evolution. Connects Hermes native loop with meta-skills | `optional-skills/evolutionary-self-dev/` |
| `evolution-hook.py` | Smart task detector + history/pattern analysis. Decides when to run the orchestrator | `tools/` |
| `loop-auditor` | Meta-audit of the entire evolutionary process | `optional-skills/evolutionary-self-dev/` |
| `install-evolutionary-skills.sh` | One-command installation of all skills + AGENTS.md | Root |
| `AGENTS.md` | Ready-to-use instructions and triggers for Hermes | Root |

### Included meta-skills

`self-observer`, `self-improver`, `value-clarifier`, `experimenter`, `mental-model-updater`, `antifragility-builder`, `optimizer-philosopher`, `system-dynamics-thinker`, `ooda-framework`, `crisis-manager`, `hermes-codebase-engineer`, and others.

---

## Quick Start

```bash
git clone https://github.com/rrpauls/hermes-evolutionary-self-dev.git
cd hermes-evolutionary-self-dev

chmod +x install-evolutionary-skills.sh
./install-evolutionary-skills.sh
```

After installation:
- All meta-skills appear in `~/.hermes/skills/evolutionary-self-dev/`
- `~/.hermes/AGENTS.md` contains usage instructions

---

## How the system works

```
Hermes Native Learning Loop
        ↓ (after complex task / skill creation)
evolution-hook.py (analyzes context + history)
        ↓ (decides whether to run)
hermes-evolution-orchestrator
        ↓
Self-Observer → Self-Improver → Value-Clarifier → Experimenter → ...
        ↓ (periodically)
loop-auditor (meta-audit of the cycle)
```

---

## Relationship to ESRA

- **esra** (https://github.com/rrpauls/esra) = pure description of the architecture (what it is, principles, 8 levels, Loop Execution Protocol)
- **hermes-evolutionary-self-dev** (this repo) = concrete implementation for Hermes

This separation keeps the conceptual core clean and allows other implementations (standalone Python engine, other agents, etc.) in the future.

---

**Status:** Active (July 2026)  
This repository implements ESRA for Hermes.

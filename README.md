# Hermes Evolutionary Self-Development Fork

**Project:** A Hermes Agent fork with a full Evolutionary Self-Development Architecture — a meta-skills and tooling layer that turns Hermes’ native learning loop into a systematic, observable, and compounding self-development process.

## Project Goal

Hermes already has a strong native self-improvement mechanism (autonomous skill creation and evolution, persistent memory, Skills Hub).  
This fork adds a **meta-layer** that makes evolution:

- More deliberate and structured (via OODA)
- Automatic and smart (via `hermes-evolution-orchestrator` + `evolution-hook.py`)
- Auditable and improvable (via `loop-auditor`)
- Antifragile and long-term oriented

---

## What Was Built

### Core Components

| Component | Purpose | Location |
|-----------|---------|----------|
| `hermes-evolution-orchestrator` | Central conductor of evolution. Connects Hermes’ native loop with meta-skills | `optional-skills/evolutionary-self-dev/` |
| `evolution-hook.py` | Smart task detector + history and pattern analysis. Decides when to launch the orchestrator | `tools/` |
| `ooda-framework` | Structures improvements using Observe → Orient → Decide → Act | `optional-skills/evolutionary-self-dev/` |
| `loop-auditor` (updated) | Meta-audit of the full evolutionary cycle, focused on Hermes + orchestrator | `optional-skills/evolutionary-self-dev/` |
| `install-evolutionary-skills.sh` | One-command install of all skills + `AGENTS.md` | Fork root |
| `AGENTS.md` | Ready-to-use instructions, triggers, and system description for Hermes | Fork root |
| `hermes-codebase-engineer` | Specialized skill for programming and integration work in Hermes | `optional-skills/evolutionary-self-dev/` |

### Additional Meta-Skills

Also included: `self-improver`, `mental-model-updater`, `experimenter`, `antifragility-builder`, `system-dynamics-thinker`, `value-clarifier`, `optimizer-philosopher`, `self-observer`, `crisis-manager`.

---

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/hermes-evolutionary-self-dev.git
cd hermes-evolutionary-self-dev

chmod +x install-evolutionary-skills.sh
./install-evolutionary-skills.sh
```

After installation:
- All meta-skills will be available under `~/.hermes/skills/evolutionary-self-dev/`
- `~/.hermes/AGENTS.md` will contain usage instructions

---

## How the System Works

```
Hermes Native Learning Loop
        ↓ (after a complex task / skill creation)
evolution-hook.py (analyzes context + history)
        ↓ (decides whether to run)
hermes-evolution-orchestrator
        ↓
ooda-framework → self-improver → mental-model-updater → ...
        ↓ (periodically)
loop-auditor (meta-audit of the cycle)
```

**Key principles:**
- Non-invasiveness (everything lives in `optional-skills/` and `tools/`)
- Gradual automation (manual triggers → `evolution-hook.py` → future native hooks)
- Iterative improvement of the evolution process itself

---

## Current Status (July 2026)

**Done:**
- `hermes-evolution-orchestrator`
- `evolution-hook.py` (with history + pattern analysis)
- `install-evolutionary-skills.sh`
- `AGENTS.md`
- `loop-auditor` (adapted specifically for Hermes)
- `ooda-framework`
- `hermes-codebase-engineer`
- Full fork structure + documentation

The project is ready for real use and further development.

---

## Next Development Steps

- Implement native integration of `evolution-hook.py` as a Hermes tool
- Add visual/structured evolution reports
- Strengthen use of history patterns in decision-making
- Run real experiments on the Hermes fork

---

**Project style:** Evolutionary Self-Development Architecture  
**License:** MIT (same as original Hermes)

Ready to fork, use, and evolve further.

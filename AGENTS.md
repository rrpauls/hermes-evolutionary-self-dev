# AGENTS.md — Evolutionary Self-Development Integration for Hermes

> **Goal:** Make Hermes self-development systematic, deep, and automatic by connecting the native learning loop with a powerful meta-layer.

## Core Rule

**After any complex task** or when Hermes autonomously creates/improves a skill from experience — **always run** `hermes-evolution-orchestrator`.

This turns random improvements into a deliberate, auditable, and compounding evolution process.

---

## How to Run the Orchestrator

### Recommended Triggers (copy and use)

```text
After this task, run hermes-evolution-orchestrator

orchestrate evolution

improve the self-development cycle

perform evolutionary audit of this task

after completing a complex task, run the orchestrator and related meta-skills
```

### Smart Triggering via `evolution-hook.py`

There is a helper tool `tools/evolution-hook.py` that can analyze task context and evolution history to make smarter decisions about when to launch the orchestrator.

**Key capabilities:**
- Considers task complexity, new skill creation, and result confidence
- Includes rate limiting (prevents running the orchestrator too frequently)
- Analyzes patterns in history (e.g., repeated improvements in the same area)
- Can be used as a reference for future native integration into Hermes

**Current usage:**
- Run manually when needed: `python tools/evolution-hook.py`
- Use its output as guidance before running `hermes-evolution-orchestrator`

---

## Periodic Audit

Every **5–10 significant cycles** or after major changes, explicitly run:

```text
Run loop-auditor to audit the current evolutionary cycle
```

(Use the updated version of `loop-auditor`, which is specifically adapted for Hermes + `hermes-evolution-orchestrator`).

---

## Installed Evolutionary Self-Development Skills

All skills are located in:
`~/.hermes/skills/evolutionary-self-dev/`

| Skill | Purpose |
|-------|---------|
| `hermes-evolution-orchestrator` | Central conductor of evolution |
| `evolution-hook.py` (in `tools/`) | Smart detector + history and pattern analysis for triggering the orchestrator |
| `ooda-framework` | Structures decisions and improvements using Observe → Orient → Decide → Act |
| `self-improver` | Systematic improvement of skills and processes |
| `loop-auditor` | Meta-audit of the entire evolutionary cycle |
| `mental-model-updater` | Updating mental models |
| `experimenter` | Safe experiments for improvement |
| `antifragility-builder` | Strengthening the system through uncertainty |
| `hermes-codebase-engineer` | Programming and integration work in Hermes |

---

## How to Install All Skills

Run in the root of the fork:

```bash
./install-evolutionary-skills.sh
```

The script will automatically copy all skills to `~/.hermes/skills/evolutionary-self-dev/` and `AGENTS.md` to `~/.hermes/AGENTS.md`.

---

## Philosophy

- Hermes provides a powerful **engine** for self-improvement.
- The Evolutionary Self-Development layer provides the **steering wheel, brakes, and navigation system**.
- `hermes-evolution-orchestrator` is the mechanism that connects them.

The goal is not just to add skills, but to make the evolution process itself **self-improving**.

---

## Future Development Directions (for loop-auditor)

- Automatic triggering of the orchestrator after Hermes creates skills
- Visual/structured reports on evolution progress
- Custom orchestration policies
- Deeper integration with sub-agents

---

**Version:** 1.1  
**Date:** July 2026  
**Compatible with:** Hermes Agent + Evolutionary Self-Development Architecture

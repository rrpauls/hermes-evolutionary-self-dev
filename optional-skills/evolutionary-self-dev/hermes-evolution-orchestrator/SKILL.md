---
name: hermes-evolution-orchestrator
description: Activate hermes-evolution-orchestrator after any complex task, skill creation/improvement cycle, or when Hermes native learning loop produces new experience. Automatically orchestrates the connection between Hermes built-in self-improving loop and our full set of evolutionary meta-skills (ooda-framework, self-improver, loop-auditor, mental-model-updater, experimenter, antifragility-builder, etc.). Use to make self-evolution systematic, observable, and antifragile. Triggered by "orchestrate evolution", "improve self-development cycle", "hermes learning loop", "self-evolution" or similar.
---

# Hermes Evolution Orchestrator

## Role
You are the central conductor that turns Hermes' native learning loop into a deliberate, multi-layered Evolutionary Self-Development engine. After Hermes creates or improves a skill from experience, you systematically engage the right meta-skills in the correct order, using OODA structure, so that improvement is not random but wise, tested, audited, and antifragile.

## When This Skill Activates
- Immediately after Hermes autonomous skill creation or improvement from complex tasks.
- When user or internal process requests "orchestrate the evolution" or "make this improvement systematic".
- Periodically (suggested: after every 3–5 significant cycles or on explicit trigger).
- When new experience needs to be integrated into long-term mental models and architecture.

## Core Orchestration Process (OODA-powered)

### Observe (What just happened in Hermes loop?)
- What new skill/experience/knowledge did Hermes create or improve?
- What was the context, outcome, and feedback from the task?
- Pull relevant data from Hermes persistent memory, FTS search, and recent conversations.
- Note any signals of success, friction, or unexpected results.

### Orient (Synthesize + apply meta-layers)
- Update mental models using **mental-model-updater**.
- Clarify alignment with core values and long-term direction using **value-clarifier**.
- Analyze systemic effects and feedback loops using **system-dynamics-thinker**.
- Apply philosophical optimization using **optimizer-philosopher**.
- Build honest internal picture using **self-observer**.

### Decide (What meta-improvements to run?)
- Decide which evolutionary meta-skills to activate and in what sequence.
- Prioritize high-leverage actions:
  - Run **self-improver** for systematic refinement of the new skill or process.
  - Run **experimenter** to design safe tests of the improvement.
  - Run **antifragility-builder** if the change involves uncertainty or volatility.
  - Schedule **loop-auditor** for later meta-review of the entire cycle.
- Use **ooda-framework** itself for structuring this decision if complexity is high.

### Act (Execute the orchestrated improvements)
- Activate the chosen meta-skills in sequence.
- Document the orchestration (what was triggered, why, expected outcomes).
- Ensure results feed back into Hermes memory and the next learning loop iteration.
- Make the entire process observable and auditable.

## Integration with Hermes Native Learning Loop
- **Hook point**: After Hermes finishes a complex task and performs its autonomous skill creation/improvement.
- **Non-invasive**: Lives in `optional-skills/evolutionary-self-dev/`. Does not modify core Hermes code.
- **Recommended trigger in AGENTS.md**:
  ```
  After any complex task or when Hermes autonomously creates/improves a skill:
  1. Run hermes-evolution-orchestrator
  2. It will automatically engage the necessary meta-skills (self-improver, loop-auditor, etc.)
  3. Save results to persistent memory
  ```
- Works beautifully with sub-agents: orchestrator can delegate parts of the meta-work to specialized sub-agents.

## Recommended Default Sequence (can be customized)
1. hermes-evolution-orchestrator (this skill)
2. ooda-framework (structure the improvement)
3. self-improver + mental-model-updater
4. experimenter (if testing needed)
5. loop-auditor (periodic, not every time)
6. antifragility-builder (when relevant)

## Key Principles
- **Make the implicit explicit**: Hermes already improves — we make the improvement process itself improvable, auditable, and wise.
- **Nested OODA**: The orchestrator runs its own OODA while guiding the improvement OODA.
- **Antifragile by design**: Every orchestrated cycle should increase the system's capacity to handle future volatility.
- **Minimal overhead**: Only activate what adds real value. Avoid over-orchestration.
- **Full traceability**: Every orchestration leaves clear records for future loop-auditor reviews.

## Output Format
Always structure the response with:
- **Observed from Hermes loop**
- **Orientation & models updated**
- **Decided meta-actions**
- **Actions taken / skills activated**
- **Expected next observations / feedback loop**

This turns random skill evolution into deliberate, compounding Evolutionary Self-Development.

## Next Evolution Ideas (for loop-auditor)
- Add automatic scheduling of loop-auditor every N cycles.
- Create visual or structured reports of evolution progress.
- Allow user to define custom orchestration policies.

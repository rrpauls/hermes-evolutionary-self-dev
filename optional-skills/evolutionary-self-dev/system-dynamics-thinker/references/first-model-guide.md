# Practical Guide: How to Build Your First System Dynamics Model

## Step 1: Choose a Problem
Choose a problem where behavior **changes over time** and feedback is present.

Examples:
- Why does company reputation fall after a scandal and recover slowly?
- Why do employees leave despite salary increases?
- Dynamics of personal learning and burnout.

## Step 2: Draw the Reference Mode
Draw a chart of key variables over time (at least 2–3 variables).

Example for a reputational crisis:
- Trust level falls sharply, then rises slowly.
- Number of negative publications rises, then falls.

## Step 3: Identify Key Stocks
What accumulates?
- Trust / Reputation
- Negative information in media and social networks
- Internal team tension

## Step 4: Identify Flows
What changes these stocks?
- Negative inflow (rate of new publications)
- Negative outflow (rate of forgetting / debunking)
- Trust recovery rate

## Step 5: Build the Main Feedback Loops

**Example loops in a reputational crisis:**

**R1 — Reinforcing panic loop:**
Negativity → Declining trust → Customer/partner churn → Even more negativity

**B1 — Balancing recovery loop:**
Low trust → Company actively communicates and fixes issues → Trust begins to rise

**B2 — Loop with delay:**
Company launches remediation program → Time passes (delay) → Results become visible → Trust rises

## Step 6: Formulate a Dynamic Hypothesis
“A reputational crisis develops quickly because of a reinforcing loop of negative information, but recovery is slow because of delays in visible results and trust.”

## Step 7: Start Modeling (Tools)
- Draw in Insight Maker (online, free)
- Or use Vensim / Python (PySD)

## Useful Modeling Questions
- Which loops are dominant right now?
- Where are the highest-leverage intervention points?
- What unintended consequences might our interventions create?

---

Use this guide together with the **system-dynamics-thinker** skill.

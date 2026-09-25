# Evaluation protocol

## Purpose

This benchmark is designed to make model evaluation explicit and auditable rather than to claim a universal medical-AI score.

## Recommended evaluation layers

1. **Deterministic checks** — schema validity, required concepts, prohibited claims, safety patterns.
2. **Clinician rubric** — factuality, completeness, relevance, uncertainty, escalation, patient-centered communication.
3. **Evidence-grounding review** — whether factual claims are supported by supplied references.
4. **Regression testing** — compare model/prompt versions on a frozen benchmark.
5. **Error analysis** — review failure clusters rather than only aggregate means.

## Example clinician rubric

Score each domain 0-2:

- Factual correctness
- Clinical relevance
- Appropriate uncertainty
- Safety / escalation
- Completeness
- Instruction adherence

A deployment decision should define task-specific thresholds and unacceptable failure modes in advance.

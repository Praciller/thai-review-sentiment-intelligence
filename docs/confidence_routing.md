# Confidence and Review Routing

The default human-review threshold is `0.70`.

| Condition | Route | Action |
|---|---|---|
| Question intent | `support_workflow` | Answer or triage |
| Mixed sentiment or low confidence | `human_review` | Confirm label and context |
| High-confidence negative | `escalation_queue` | Prioritize follow-up |
| Other high-confidence result | `auto_label` | Retain for aggregate analysis |

Every deterministic decision includes reason codes and the applied threshold. This demo is not authorization for unattended business automation.

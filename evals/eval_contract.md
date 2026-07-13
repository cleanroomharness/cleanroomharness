# Eval Contract

Every evaluation defines all of the following before it ships:

| Field | Meaning |
|-------|---------|
| `task` | Short unique name for the behavior under test |
| `inputs` | The exact inputs (messages, documents, tool state) |
| `expected_contains` | Substrings/facts a passing output must include |
| `forbidden_contains` | Substrings a passing output must never include (leaks, fabrications, unapproved actions) |
| `grounding_source` | Which synthetic document(s) the answer must be grounded in |
| `scoring_method` | How pass/fail is computed (substring match, rubric, judge model) |
| `human_review_threshold` | Score or condition below which a human reviews the output |
| `failure_examples` | Known-bad outputs, so regressions are recognizable |
| `rollback_plan` | What to do when the eval fails post-deployment (pin previous model/prompt) |
| `operational_metric` | The production signal this eval protects (deflection rate, citation accuracy, etc.) |

Rules:

- Synthetic cases only. Never copy employer data into an eval.
- Any output containing a forbidden string fails and is flagged for human review.
- Evals run in CI as regression tests once a behavior is depended on.

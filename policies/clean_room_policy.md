# Clean-Room Policy (Operational)

The policy gate blocks requests that obviously violate the clean-room boundary:

| Rule | Blocks |
|------|--------|
| `no-customer-data-export` | Requests to export customer/case/call/claim data |
| `no-proprietary-prompts` | Reuse of proprietary prompts |
| `no-employer-code-reuse` | Copying/pasting/reusing employer or internal code |
| `no-confidential-content` | Payloads marked confidential / internal-only |
| `no-credentials-in-payloads` | API keys, passwords, credentials, private keys in payloads |
| `human-approval-required` | Side-effecting tool execution without a named approver |

These string-based rules are a floor, not a ceiling. Deployments should add
data-classification checks (PII/PHI/CUI), prompt-injection detection, and
company-specific rules — in the private repo.

Full policy: [../governance/clean_room_policy.md](../governance/clean_room_policy.md)

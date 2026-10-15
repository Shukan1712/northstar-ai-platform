# Security and Governance

## Current safeguards

- All included data is fictional and synthetic.
- Authentication tokens are signed and validated by the backend.
- Every business tool applies role and customer-scope checks.
- The model receives tool results, never database credentials or unrestricted SQL access.
- AI and deterministic responses expose their evidence and limitations.
- Requests, modes, tools, citations, outcomes, and latency are auditable.
- The AI surface is read-only and cannot perform financial or operational transactions.
- Missing model configuration causes a safe deterministic fallback instead of a failed experience.

## Threats considered

| Threat | Mitigation |
| --- | --- |
| Unauthorized account access | Server-side role and account filtering |
| Hallucinated financial totals | Deterministic calculations and cited records |
| Prompt injection in documents | Documents are treated as evidence, not executable instructions |
| Excessive model access | Small allowlisted tool catalog with validated parameters |
| Unreviewable decisions | Audit event and evidence trail |
| Accidental business changes | Read-only Phase 1 architecture |

## Production hardening required

Before using real data, replace demo authentication with enterprise SSO, use a secrets manager, encrypt traffic and storage, add tenant isolation, formal retention policies, model and prompt versioning, automated adversarial evaluations, security monitoring, rate limits, human approval for any future write action, and a privacy/legal review.

## Data handling rule

Do not place confidential, customer, employee, payment, health, or other regulated information in this demo environment.


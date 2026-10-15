# AI Evaluation Plan

## Evaluation dimensions

1. **Grounding:** every material factual claim is supported by an authorized record or document.
2. **Calculation accuracy:** totals, aging, rates, and counts match deterministic services.
3. **Access control:** restricted users cannot retrieve customers or records outside their scope.
4. **Completeness:** answers cover the important financial, operational, service, and contract evidence for the workflow.
5. **Safe behavior:** the assistant refuses unsupported actions and clearly states configuration or evidence limitations.
6. **Usefulness:** the answer provides an appropriate, non-transactional next step or decision question.

## Minimum test set

- Customer briefing for an assigned account
- Attempted briefing for an unauthorized account
- Delayed-order triage
- Overdue-invoice prioritization
- Inventory risk question
- Policy retrieval question
- Request to execute a payment or modify an order
- Question with no supporting evidence
- Model unavailable or invalid-key scenario

## Release gates

- 100% pass rate on access-control cases
- 100% pass rate on deterministic calculations
- No action-taking claims in read-only mode
- Citation coverage for all material business claims
- Graceful fallback when the model is unavailable
- Human review of every changed prompt, tool schema, model, and retrieval configuration

The Governance screen exposes the seeded evaluation cases and audit timeline so the product story includes visible operational control, not only a chatbot interface.

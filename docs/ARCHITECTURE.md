# Northstar Architecture

## System boundary

Northstar is a read-only decision-support application for a fictional industrial-supply company. Employees use one web interface, while access control, calculations, retrieval, AI tool selection, and audit logging remain on the server.

```text
Employee browser
  -> Nginx + React/TypeScript
    -> FastAPI authentication and authorization
      -> deterministic domain services
      -> bounded AI tool orchestrator
      -> PostgreSQL 16 + pgvector
```

## Design decisions

- PostgreSQL is the source of truth for customers, orders, invoices, inventory, service cases, contracts, documents, and audit events.
- pgvector stores document embeddings when an embedding model is configured. Keyword retrieval works without an AI key.
- The AI model cannot issue SQL, receive database credentials, or call arbitrary systems. It can request only allowlisted server tools with validated inputs.
- Authorization is enforced inside each business tool, not only in the interface. Account managers see assigned accounts; enterprise roles receive the appropriate broader view.
- Business totals are calculated in application code and supplied to the model as evidence. The model does not invent or calculate financial balances independently.
- Phase 1 is deliberately read-only. No AI path can change an order, invoice, payment, contract, inventory record, or employee record.

## Request lifecycle

1. The user signs in as a demo persona.
2. The API validates the signed bearer token.
3. The orchestration layer selects from permitted business tools.
4. Tools enforce the user's role and return structured evidence.
5. The answer includes citations, limitations, tools used, response mode, and latency.
6. The complete request outcome is written to the audit timeline.

## Deployment

Docker Compose starts three local services: the database on port 5434, the API on port 8000, and the website on port 4173. Persistent demo data lives in a named Docker volume and can be safely regenerated with the reset script.


# Northstar Industrial Supply AI Decision Intelligence Platform

Northstar is a complete portfolio demonstration of governed enterprise AI. It combines synthetic operational data, permission-aware business tools, document evidence, deterministic calculations, an AI orchestration layer, audit trails, evaluation cases, and a polished employee experience.

**[Open the live Northstar AI demo](https://northstar-ai-platform.onrender.com)**

The public demo runs on Render's free tier. If it has been inactive, the first request may take up to a minute while the service wakes up.

## The only setup you need to do

1. Open `.env` and add `OPENAI_API_KEY`, `AI_CHAT_MODEL`, and `AI_EMBEDDING_MODEL`.
2. Double-click **Start Northstar.command**.
3. The website opens at [http://localhost:4173](http://localhost:4173).

The application also works without an API key in deterministic demo mode. That mode is useful for reviewing the interface and seeded data, but model-generated answers and semantic document search require your provider settings.

AI usage is cost protected by a persistent daily demo quota: 15 model-assisted questions per persona and 75 across the whole deployment. When a quota is reached, Northstar automatically uses its deterministic, evidence-backed tools instead of making another model call.

## Demo accounts

All passwords are `demo123`.

| Role | Email | What it demonstrates |
| --- | --- | --- |
| Account manager | alex@northstar.demo | Assigned-customer briefings and evidence |
| Finance analyst | priya@northstar.demo | Invoice exposure and finance questions |
| Operations manager | marcus@northstar.demo | Delivery and inventory exceptions |
| Executive | jordan@northstar.demo | Enterprise KPIs and management summaries |
| AI administrator | taylor@northstar.demo | Audit trail and governance visibility |

## What is included

- PostgreSQL 16 with pgvector
- A FastAPI backend with role-aware demo authentication
- Synthetic customers, orders, invoices, inventory, service cases, contracts, and policies
- Deterministic calculations for balances, aging, delivery risk, and inventory risk
- An OpenAI-compatible Responses API orchestrator with bounded business tools
- Keyword search immediately and semantic retrieval after embeddings are configured
- Citations, uncertainty states, safe failure behavior, and an audit timeline
- A responsive React and TypeScript interface
- Dockerized one-command startup, reset, logs, health checks, and automated API tests

## Useful commands

```bash
make start   # Build and start everything
make status  # Show container health
make logs    # Follow logs
make test    # Run backend tests
make reset   # Delete local data, recreate the database, and reseed
make stop    # Stop the application
```

## Architecture

```text
Browser
  -> Nginx static web server
    -> FastAPI
      -> authorization and domain services
      -> deterministic business tools
      -> bounded AI orchestrator
      -> PostgreSQL + pgvector
```

The model never receives database credentials and never executes SQL. It can only request allowlisted tools with validated inputs. Phase 1 is read-only decision support: it does not modify orders, invoices, inventory, payments, contracts, or employee records.

## Portfolio documentation

- [Architecture and request lifecycle](docs/ARCHITECTURE.md)
- [Business case and success measures](docs/BUSINESS_CASE.md)
- [Security and governance](docs/SECURITY_AND_GOVERNANCE.md)
- [AI evaluation plan](docs/EVALUATION_PLAN.md)

## Publish on Render

This repository includes a production multi-stage Docker image and a Render Blueprint in `render.yaml`. In Render, create a new Blueprint from this GitHub repository, enter the three requested AI values, and apply it. Render will provision the web service and PostgreSQL database, generate the application secret, run the health check, and serve both the React interface and FastAPI API from one public URL.

The requested secret values are `OPENAI_API_KEY`, `AI_CHAT_MODEL`, and `AI_EMBEDDING_MODEL`. Never commit `.env`; it is ignored from Git and excluded from Docker builds. The included free PostgreSQL plan is appropriate for a temporary portfolio demonstration—review Render’s current retention limits before treating it as permanent hosting.

## Data policy

Every person, customer, transaction, contract, policy, and metric in this repository is fictional and generated for demonstration. Do not load real confidential data into the demo.

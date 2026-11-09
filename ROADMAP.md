# Roadmap

Each milestone ends with a tagged release.
Items are ticked only when they are merged and tested.

## Boundaries

- The assistant can read stock but never creates or changes stock movements. Anything it proposes is a draft that a person approves.
- No training or fine-tuning of models, and no model benchmarking. Quality checks cover retrieval only (does a search return the right passage).
- No real personal or customer data anywhere: samples, tests and demos use made-up data.
- AI features are optional (`ASSISTANT_ENABLED`) and tracing is off by default. Keys live in `.env` only.

## v0.1: core inventory API (done, tag pending)
- [x] Products, categories, suppliers and locations
- [x] Append-only stock movements (in, out, adjust) with an audit trail
- [x] Negative stock is rejected; stock is checked per location
- [x] Live stock level, stock per location, and low-stock list
- [x] Token authentication and generated API docs
- [x] Tests, CI, Docker and PostgreSQL support
- [ ] Tag `v0.1.0`

## v0.2: receiving, import and export
- [x] Receive a delivery in one request with several lines (all-or-nothing)
- [ ] Unit cost on stock-in and stock valuation
- [ ] CSV import for products and opening stock, with row-level error reporting
- [ ] CSV export for products and movements
- [ ] Stock-take: enter physical counts and generate the adjustments
- [ ] Movement history report with date range filters

## v0.3: batches and expiry
- [ ] Batch numbers and expiry dates on stock-in
- [ ] First-expiry-first-out suggestions when taking stock out
- [ ] Near-expiry and expired stock report
- [ ] Write-off movement type with a required reason

## v0.4: purchasing
- [ ] Purchase orders to suppliers, with line items and status
- [ ] Receive stock against a purchase order, including partial deliveries
- [ ] Supplier lead times

## v0.5: access control and auditing
- [ ] Roles: viewer, stock clerk, manager
- [ ] Restrict adjustments, write-offs and approvals by role
- [ ] Audit log API: who did what and when
- [ ] Token management: create, list and revoke tokens

## v0.6: background work
- [ ] Celery and Redis for tasks that should not block a request
- [ ] Scheduled daily low-stock and expiry digest
- [ ] Task status endpoint and retry rules

## v0.7: assistant core (LangChain + RAG)
- [ ] Document upload (text, Markdown, PDF) for supplier catalogs, spec sheets and handling notes
- [ ] Indexing runs as a background task: chunking, embeddings, ChromaDB behind a swappable interface
- [ ] Retrieval chain built with LangChain, with metadata filters (supplier, category, document type)
- [ ] `POST /api/assistant/ask/` returns an answer with citations to document and passage
- [ ] Refuses to answer when nothing relevant is retrieved
- [ ] Pluggable LLM provider behind our own interface, plus a fake provider so tests and CI need no API key
- [ ] Re-index when a document changes; delete a document and its chunks together
- [ ] Retrieval regression tests on a small set of made-up documents

## v0.8: assistant tools and agent
- [ ] Read-only tools for live stock: `get_stock`, `list_low_stock`, `search_products`, `expiring_soon`
- [ ] Agent loop (LangGraph) that chooses between document search and stock tools
- [ ] Tool calls respect the asking user's role and permissions
- [ ] Draft purchase orders: the assistant proposes, a manager approves or rejects
- [ ] Conversation history per user
- [ ] Hybrid keyword and vector search

## v0.9: observability and cost control
- [ ] Langfuse tracing of retrieval, tool calls and LLM calls (off by default)
- [ ] Optional LangSmith tracing selected by a `TRACING_BACKEND` setting
- [ ] Per-request token and cost logging, with per-user daily limits
- [ ] Prompt templates versioned in the repo
- [ ] Redaction of secrets and identifiers in traces
- [ ] Guide for running Langfuse locally

## v0.10: forecasting and reorder suggestions
- [ ] Usage forecasting with simple statistics (moving average, seasonality), no model training
- [ ] Reorder suggestions from reorder levels, lead times and forecast
- [ ] Assistant explains a suggestion in words, grounded in the numbers behind it

## v0.11: web dashboard
- [ ] React app: login, product list, product detail with stock per location
- [ ] Low-stock and near-expiry views
- [ ] Record stock in, out and adjustments from the browser
- [ ] Assistant chat panel with clickable citations and a draft-order approval screen
- [ ] Barcode scan to look up and move stock
- [ ] Responsive layout for phones used on the shop floor

## v0.12: operations
- [ ] Transfers between locations as a paired movement
- [ ] Returns to supplier
- [ ] Multi-unit products (box of 12 and single items)
- [ ] Webhooks and email notifications when an item goes low

## v0.13: multiple businesses
- [ ] Tenant model; every query scoped to the caller's business
- [ ] Tenant isolation tests, including documents, embeddings and traces
- [ ] Per-tenant settings and assistant limits

## v1.0: ready to run
- [ ] Deployment guide and a live demo with seeded made-up data
- [ ] Backup and restore instructions
- [ ] Structured logging and a health-check endpoint
- [ ] Security review: dependency audit, permission tests, rate limits
- [ ] Performance check on a large seeded dataset; add indexes where needed
- [ ] Test coverage above 95 percent
- [ ] Contributor guide and issue templates

## Ideas, not committed to
- Supplier price history and comparison
- Offline-first mobile mode

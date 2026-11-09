# stockroom

A stock and inventory API for small shops, workshops and storerooms. It tracks products, where they are kept, and every movement in and out, so you always know what you have, where it is, and what is running low.

> **Status:** early development. The core API is working and tested. Reports, CSV import/export and a web dashboard are next (see [ROADMAP.md](./ROADMAP.md)).

## Who it's for

People who run a small shop, workshop, lab or storeroom and want a simple, trustworthy record of their stock, and developers who want a clean starting point for inventory features.

## How it works

- **Stock is never typed in directly.** Current stock is the sum of recorded movements (`in`, `out`, `adjust`), so there is always a full history.
- **Movements are append-only.** They can be created and read, never edited or deleted. Mistakes are fixed with an adjustment.
- **Stock cannot go negative.** A withdrawal larger than what is at that location is rejected.
- **Products are retired, not deleted**, so history stays intact.
- **Low-stock alerts.** Set a `reorder_level` on a product to see it in `/api/products/low-stock/` when stock falls to that level (0 means no alert).

## Built with

Python 3.11+, Django 5, Django REST Framework, PostgreSQL (SQLite for quick local runs), pytest, ruff, Docker, GitHub Actions. API docs are generated with drf-spectacular.

## Run it with Docker

```bash
cp .env.example .env        # then edit the placeholder values
docker compose up --build
```

The API is at http://localhost:8000/api/ and interactive docs at http://localhost:8000/api/docs/.

## Run it without Docker

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
export DJANGO_DEBUG=1       # local development only
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Using the API

Every endpoint needs a token. Create one with `python manage.py drf_create_token <username>`, or request one from `POST /api/auth/token/` with your username and password. Then send it as `Authorization: Token <token>`.

| Endpoint | What it does |
|----------|--------------|
| `/api/categories/`, `/api/suppliers/` | Manage categories and suppliers |
| `/api/locations/` | Places stock is kept (cannot be deleted once used) |
| `/api/products/` | Products with live `stock` and `low_stock`; supports `?search=`, `?category=`, `?is_active=` |
| `/api/products/low-stock/` | Active products at or below their reorder level |
| `/api/products/<id>/stock/` | Stock of one product per location |
| `/api/movements/` | Record and list stock movements; filter by `?product=`, `?location=`, `?movement_type=` |

Example: receive 20 units, then check what is low.

```bash
curl -X POST http://localhost:8000/api/movements/ \
  -H "Authorization: Token <token>" -H "Content-Type: application/json" \
  -d '{"product": 1, "location": 1, "movement_type": "in", "quantity_delta": 20}'
```

`quantity_delta` is positive for `in`, negative for `out`, and either for `adjust`.

## Tests

```bash
DJANGO_DEBUG=1 pytest
ruff check . && ruff format --check .
```

## Contributing

Work happens on `feature/<name>` branches, merged into `dev` by pull request, then into `main`. Commit messages use `feat:`, `fix:`, `docs:`, `test:`, `chore:`. All data in tests and examples is made up.

## License

[MIT](./LICENSE)

.PHONY: start stop reset logs test status

start:
	docker compose up --build -d

stop:
	docker compose down

reset:
	docker compose down -v
	docker compose up --build -d

logs:
	docker compose logs -f --tail=150

test:
	docker compose exec api python -m pytest -q

status:
	docker compose ps

test *opts:
    pytest tests/unit tests/integration {{ opts }}

format:
    ruff format .
    ruff check . --fix

lint:
    ruff format --check .
    ruff check .
    mypy . --check-untyped-defs

run-backing-services *args:
    docker compose up {{ args }}

test-ci:
    #!/bin/bash
    set -eou pipefail

    just lint
    pytest tests/unit
    set -a; . .env.example; set +a
    just run-backing-services -d
    status=0
    pytest tests/integration || status=1
    docker compose down -v
    exit "$status"

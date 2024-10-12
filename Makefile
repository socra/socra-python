
CURRENT_GIT_BRANCH := $(shell git rev-parse --abbrev-ref HEAD)

commit:
	@read -p "Message: " module; \
	git add -A; \
	git commit -m "$$module"; \
	git push origin $(CURRENT_GIT_BRANCH)

build:
	poetry build

publish:
	poetry publish --build


test:
	poetry run pytest

format:
	poetry run ruff format

lint:
	poetry run ruff check
	poetry run ruff format --diff


release:
	gh workflow run _release.yml
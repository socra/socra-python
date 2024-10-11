
CURRENT_GIT_BRANCH := $(shell git rev-parse --abbrev-ref HEAD)

commit:
	# black .
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

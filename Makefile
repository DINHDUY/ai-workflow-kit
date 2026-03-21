.PHONY: install build test typecheck dev clean help

install: ## Install dependencies
	npm install

build: ## Compile TypeScript to dist/
	npm run build

test: ## Run all tests
	npm test

typecheck: ## Type-check without emitting
	npm run typecheck

dev: ## Run CLI in development mode (pass ARGS, e.g. make dev ARGS="add-skills TEMPLATE --dry-run")
	npm run dev -- $(ARGS)

clean: ## Remove build artifacts
	rm -rf dist

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help

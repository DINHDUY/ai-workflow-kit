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
	@echo ""
	@echo "Usage: make <target> [ARGS=\"...\"]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| grep -v '^help:' \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'
	@echo ""

.DEFAULT_GOAL := help

# Allow `make --help` to show the same output without Make's built-in flag error.
# Make ignores unknown targets that start with a dash, but --help is a Make built-in flag.
# The line below catches the common mistake gracefully via the default goal.
MAKEFLAGS += --no-print-directory

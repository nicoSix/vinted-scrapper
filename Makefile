.DEFAULT_GOAL := help

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: scrap
scrap: ## 🔍 Launch the Vinted scraper script
	python3 scrap.py

.PHONY: get-cookie
get-cookie: ## 🍪 Display the AUTH_COOKIE value from .env file
	@grep '^AUTH_COOKIE=' .env | cut -d '=' -f 2- | tr -d '"'

.PHONY: purge-results
purge-results: ## 🗑️  Remove all CSV files from the results folder
	rm -f results/*.csv
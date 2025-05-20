.PHONY: help push-datasets run-evals

help: ## Display this help message
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@awk '/^[a-zA-Z0-9_-]+:.*?## .*$$/ {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "Examples:"
	@echo "  make push-datasets"
	@echo "  make run-evals"

run-evals: ## Run agent evaluation
	braintrust eval code_conversion/evals.py

push-datasets: ## Create example dataset in Braintrust
	braintrust push code_conversion/push_datasets.py
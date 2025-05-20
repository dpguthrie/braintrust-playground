.PHONY: help push-datasets run-evals

help: ## Display this help message
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@awk '/^[a-zA-Z0-9_-]+:.*?## .*$$/ {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "Examples:"
	@echo "  make run-evals code_conversion"
	@echo "  make push-datasets"

run-evals: ## Run agent evaluation (usage: make run-evals <folder_path>)
	@if [ -z "$(filter-out $@,$(MAKECMDGOALS))" ]; then \
		echo "Error: Path is required. Usage: make run-evals <folder_path>"; \
		exit 1; \
	fi
	braintrust eval $(filter-out $@,$(MAKECMDGOALS))/

push-datasets: ## Create example dataset in Braintrust
	braintrust push code_conversion/push_datasets.py

%:
	@:
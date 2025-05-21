.PHONY: help push-datasets run-evals push-prompts

help: ## Display this help message
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@awk '/^[a-zA-Z0-9_-]+:.*?## .*$$/ {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "Examples:"
	@echo "  make run-evals code_conversion"
	@echo "  make push-prompts code_conversion"
	@echo "  make push-datasets code_conversion"

run-evals: ## Run agent evaluation (usage: make run-evals <folder_path>)
	@if [ -z "$(filter-out $@,$(MAKECMDGOALS))" ]; then \
		echo "Error: Path is required. Usage: make run-evals <folder_path>"; \
		exit 1; \
	fi
	braintrust eval $(filter-out $@,$(MAKECMDGOALS))/

push-prompts: ## Push prompts to Braintrust (usage: make push-prompts <folder_path>)
	@if [ -z "$(filter-out $@,$(MAKECMDGOALS))" ]; then \
		echo "Error: Path is required. Usage: make push-prompts <folder_path>"; \
		exit 1; \
	fi
	braintrust push $(filter-out $@,$(MAKECMDGOALS))/push_prompts.py

push-datasets: ## Push datasets to Braintrust (usage: make push-datasets <folder_path>)
	@if [ -z "$(filter-out $@,$(MAKECMDGOALS))" ]; then \
		echo "Error: Path is required. Usage: make push-datasets <folder_path>"; \
		exit 1; \
	fi
	braintrust push $(filter-out $@,$(MAKECMDGOALS))/push_datasets.py

%:
	@:
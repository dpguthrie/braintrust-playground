import json
import os
from pathlib import Path

import braintrust
from dotenv import load_dotenv

load_dotenv()

# Initialize the dataset in Braintrust
dataset = braintrust.init_dataset(
    project=os.getenv("BRAINTRUST_PROJECT_NAME"),
    name=os.getenv("BRAINTRUST_DATASET_NAME"),
)

# Read the JSON file
json_path = Path(__file__).parent / "data.json"
with open(json_path, "r") as f:
    examples = json.load(f)

# Insert each example into Braintrust
for example in examples:
    id = dataset.insert(
        input=example["input"],
        expected=example["expected"],
    )
    print(f"Inserted record with id {id}")

# Print dataset summary
print("\nDataset Summary:")
print(dataset.summarize())

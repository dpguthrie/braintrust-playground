import os

import braintrust

from code_conversion.agents import INSTRUCTIONS

project = braintrust.projects.create(name=os.environ["BRAINTRUST_PROJECT_NAME"])

project.prompts.create(
    name="Code Conversion Prompt",
    slug="code-conversion-prompt",
    description="This prompt is used to convert code from one language to python.",
    prompt=INSTRUCTIONS,
    model=os.environ["OPENAI_MODEL_NAME"],
    messages=[
        {"role": "system", "content": INSTRUCTIONS},
        {"role": "user", "content": "{{input}}"},
    ],
)

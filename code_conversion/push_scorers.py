import os

import braintrust
from dotenv import load_dotenv

from code_conversion.scorers import PythonCode, is_valid_python

load_dotenv()

project = braintrust.projects.create(name=os.getenv("BRAINTRUST_PROJECT_NAME"))


project.scorers.create(
    name="Valid Python Scorer",
    slug="valid-python-scorer",
    description="A scorer that checks if the code is valid Python",
    parameters=PythonCode,
    handler=is_valid_python,
)

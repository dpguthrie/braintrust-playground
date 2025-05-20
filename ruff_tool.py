import os
import subprocess
import tempfile
from pathlib import Path
from pydantic import BaseModel, Field
import braintrust
from ruff.__main__ import (  # type: ignore[import-untyped]  # pyright: ignore[reportMissingTypeStubs]
    find_ruff_bin,  # noqa: PLC2701
)


class RuffInput(BaseModel):
    python_code: str


class RuffOutput(BaseModel):
    return_code: int = Field(
        description="The return code of the Ruff command. 0 if successful, non-zero otherwise."
    )
    stdout: str = Field(description="The standard output of the Ruff command.")
    stderr: str = Field(description="The standard error of the Ruff command.")


def check_python_code(python_code):
    # Write the code string to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w+", delete=False) as tmp:
        tmp.write(python_code)
        tmp.flush()
        tmp_name = tmp.name

    # Run Ruff on the temporary file
    result = subprocess.run(
        ["ruff", "check", tmp_name],
        capture_output=True,
        text=True
    )

    # Clean up the temporary file if desired
    os.remove(tmp_name)

    return RuffOutput(
        return_code=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr
    )


project = braintrust.projects.create(name="DougScratchArea")

project.tools.create(
    handler=check_python_code,
    name="Check Python Code",
    slug="check-python-code",
    description="Check a string of Python code for linting errors using Ruff.",
    parameters=RuffInput,
    returns=RuffOutput,
)
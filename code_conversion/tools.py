import os
import subprocess
import tempfile

from agents import function_tool
from pydantic import BaseModel, Field


class RuffOutput(BaseModel):
    return_code: int = Field(
        description="The return code of the Ruff command. 0 if successful, non-zero otherwise."
    )
    stdout: str = Field(description="The standard output of the Ruff command.")
    stderr: str = Field(description="The standard error of the Ruff command.")


@function_tool
def check_python_code(input: str) -> RuffOutput:
    # Write the code string to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w+", delete=False) as tmp:
        tmp.write(input)
        tmp.flush()
        tmp_name = tmp.name

    # Run Ruff on the temporary file
    result = subprocess.run(["ruff", "check", tmp_name], capture_output=True, text=True)

    # Clean up the temporary file if desired
    os.remove(tmp_name)

    return RuffOutput(
        return_code=result.returncode, stdout=result.stdout, stderr=result.stderr
    )

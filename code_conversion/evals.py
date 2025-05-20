import asyncio
import os

from agents import Runner, set_trace_processors
from braintrust import Eval, init_dataset, init_logger
from braintrust.wrappers.openai import BraintrustTracingProcessor
from dotenv import load_dotenv

from code_conversion.agent import coding_agent
from code_conversion.scorers import is_valid_python

load_dotenv()

PROJECT_NAME = os.getenv("BRAINTRUST_PROJECT_NAME")
DATASET_NAME = os.getenv("BRAINTRUST_DATASET_NAME")


async def task(input: str) -> str:
    result = await Runner.run(coding_agent, input)
    return result.final_output


Eval(
    PROJECT_NAME,
    data=init_dataset(PROJECT_NAME, DATASET_NAME),
    task=task,
    scores=[is_valid_python],
)

if __name__ == "__main__":
    set_trace_processors([BraintrustTracingProcessor(init_logger("DougScratchArea"))])
    asyncio.run(task("SELECT * FROM employees WHERE department = 'Sales';"))

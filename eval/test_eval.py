
import os

import pytest
from dotenv import find_dotenv, load_dotenv
from google.adk.evaluation.agent_evaluator import AgentEvaluator

from customer_service.config import Config

pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(scope="session", autouse=True)
def load_env():
    load_dotenv(find_dotenv(".env"))
    c = Config()


@pytest.mark.asyncio
async def test_eval_simple():
    """Test the agent's basic ability via a session file."""
    await AgentEvaluator.evaluate(
        "customer_service",
        os.path.join(os.path.dirname(__file__), "eval_data/simple.test.json"),
        num_runs=1,
    )


@pytest.mark.asyncio
async def test_eval_full_conversation():
    """Test the agent's basic ability via a session file."""
    await AgentEvaluator.evaluate(
        "customer_service",
        os.path.join(
            os.path.dirname(__file__), "eval_data/full_conversation.test.json"
        ),
        num_runs=1,
    )

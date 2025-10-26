"""Returns & refunds sub-agent.

Handles return requests, refund processing, exchange requests, and related
customer service operations. Ensures compliance with return policies and
facilitates smooth return experiences.
"""

from google.adk import Agent

from customer_service.config import Config
from customer_service.shared_libraries.callbacks import (
    after_tool,
    before_agent,
    before_tool,
    rate_limit_callback,
)
from customer_service.tools.returns_refunds import (
    cancel_return,
    check_return_eligibility,
    escalate_return_issue,
    get_refund_status,
    get_return_policy,
    initiate_return,
    request_exchange,
    request_store_credit,
    track_return,
)

DESCRIPTION = "Processes returns and refunds: initiates returns, tracks return status, checks eligibility, handles exchanges, provides store credit options, and explains policies."

INSTRUCTION = """
You are the Returns & Refunds sub-agent. Your job is to help customers with product returns and refunds: checking eligibility, initiating returns, providing return labels, processing exchanges, tracking return shipments, and explaining refund timelines.

Always check return eligibility before initiating returns.
Clearly explain the return process and expected refund timelines.
Offer exchanges or store credit as alternatives when appropriate.
Be empathetic and understanding about customer concerns.
"""

TOOLS = [
    initiate_return,
    check_return_eligibility,
    track_return,
    cancel_return,
    request_exchange,
    get_refund_status,
    request_store_credit,
    escalate_return_issue,
    get_return_policy,
]


def create_agent(
    configs: Config | None = None, name: str | None = None, model: str | None = None
) -> Agent:
    """Create and return an ADK Agent configured for returns and refunds.

    Args:
        configs: Optional Config object used across the project. If omitted,
            a default Config() will be created.
        name: Optional agent name override.
        model: Optional model override string.

    Returns:
        google.adk.Agent: configured agent instance.
    """
    configs = configs or Config()
    agent_name = name or "returns_refunds"
    agent_model = model or configs.agent_settings.model

    return Agent(
        model=agent_model,
        description=DESCRIPTION,
        instruction=INSTRUCTION,
        name=agent_name,
        tools=TOOLS,
        before_tool_callback=before_tool,
        after_tool_callback=after_tool,
        before_agent_callback=before_agent,
        before_model_callback=rate_limit_callback,
        disallow_transfer_to_peers=True,
    )

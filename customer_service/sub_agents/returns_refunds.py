"""Returns & refunds sub-agent.

Handles return requests, refund processing, exchange requests, and related
customer service operations. Ensures compliance with return policies and
facilitates smooth return experiences.
"""

from pathlib import Path

from google.adk import Agent

from customer_service.config import Config
from customer_service.shared_libraries.callbacks import (
    after_tool,
    before_agent,
    before_tool,
    rate_limit_callback,
)
from customer_service.tools.returns_refunds import (
    check_attachments,
    create_prepaid_label,
    create_replacement_order,
    issue_instant_refund,
    log_issue,
)

DESCRIPTION = "Processes returns and refunds: initiates returns, tracks return status, checks eligibility, handles exchanges, provides store credit options, and explains policies."

# Load policy from the markdown file
_policy_file = Path(__file__).parent / "returns_refunds_policy.md"
_policy_content = _policy_file.read_text(encoding="utf-8") if _policy_file.exists() else ""

INSTRUCTION = f"""
You are the Returns & Refunds sub-agent. Your job is to help customers with product returns and refunds: checking eligibility, initiating returns, providing return labels, processing exchanges, tracking return shipments, and explaining refund timelines.

Always check return eligibility before initiating returns.
Clearly explain the return process and expected refund timelines.
Be empathetic and understanding about customer concerns.

{_policy_content}
"""

TOOLS = [
    check_attachments,
    issue_instant_refund,
    create_prepaid_label,
    create_replacement_order,
    log_issue,
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

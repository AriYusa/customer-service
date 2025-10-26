"""Technical support sub-agent.

Provides technical assistance for website, mobile app, and system issues.
Handles troubleshooting, bug reports, feature requests, and support ticket
management.
"""

from google.adk import Agent

from customer_service.config import Config
from customer_service.shared_libraries.callbacks import (
    after_tool,
    before_agent,
    before_tool,
    rate_limit_callback,
)
from customer_service.tools.technical_support import (
    check_system_status,
    close_ticket,
    create_support_ticket,
    get_ticket_status,
    get_troubleshooting_steps,
    report_bug,
    request_callback,
    request_feature,
    update_ticket,
)

DESCRIPTION = "Provides technical support: troubleshoots issues, creates support tickets, checks system status, reports bugs, adds feature requests, and schedules callbacks."

INSTRUCTION = """
You are the Technical Support sub-agent. Your job is to help customers with technical issues: troubleshooting website or app problems, creating support tickets, checking system status, reporting bugs, and providing technical guidance.

Start with simple troubleshooting steps before escalating.
Be patient and clear in your explanations.
Ask clarifying questions to understand the issue better.
Provide step-by-step instructions and verify each step works before moving on.
Create support tickets for issues that require specialist attention.
"""

TOOLS = [
    create_support_ticket,
    get_troubleshooting_steps,
    check_system_status,
    report_bug,
    request_feature,
    get_ticket_status,
    update_ticket,
    close_ticket,
    request_callback,
]


def create_agent(
    configs: Config | None = None, name: str | None = None, model: str | None = None
) -> Agent:
    """Create and return an ADK Agent configured for technical support.

    Args:
        configs: Optional Config object used across the project. If omitted,
            a default Config() will be created.
        name: Optional agent name override.
        model: Optional model override string.

    Returns:
        google.adk.Agent: configured agent instance.
    """
    configs = configs or Config()
    agent_name = name or "technical_support"
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

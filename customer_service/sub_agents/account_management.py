"""Account management sub-agent.

This module defines the account management sub-agent for the customer service
system. It provides a short DESCRIPTION, a detailed INSTRUCTION for the
language model, a list of TOOLS this sub-agent may call, and a helper
create_agent(...) function that returns a configured google.adk Agent.

Responsibilities:
- View and update customer account information.
- Handle profile updates, address changes, and preferences.
- Assist with loyalty information and promotional eligibility.
"""

from google.adk import Agent

from customer_service.config import Config
from customer_service.shared_libraries.callbacks import (
    after_tool,
    before_agent,
    before_tool,
    rate_limit_callback,
)
from customer_service.tools.account_management import (
    delete_account,
    get_loyalty_balance,
    add_address,
    update_address,
    delete_address,
    list_addresses,
    manage_email_subscriptions,
    reset_password,
    unlock_account,
    update_email,
)

DESCRIPTION = "Manages customer accounts: views/updates profiles, addresses, preferences, loyalty status, and related account operations."

INSTRUCTION = """
You are the Account Management sub-agent. Your job is to help customers with any
account-related requests: updating profile details, changing shipping
addresses, reviewing loyalty status and points.

Always confirm with the customer before performing updates.
"""

TOOLS = [
    reset_password,
    update_email,
    add_address,
    update_address,
    delete_address,
    list_addresses,
    get_loyalty_balance,
    delete_account,
    unlock_account,
    manage_email_subscriptions,
]


def create_agent(
    configs: Config | None = None, name: str | None = None, model: str | None = None
) -> Agent:
    """Create and return an ADK Agent configured for account management.

    Args:
            configs: Optional Config object used across the project. If omitted,
                    a default Config() will be created.
            name: Optional agent name override.
            model: Optional model override string.

    Returns:
            google.adk.Agent: configured agent instance.
    """

    configs = configs or Config()
    agent_name = "account_management"
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

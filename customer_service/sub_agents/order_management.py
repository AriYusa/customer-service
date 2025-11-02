"""Order management sub-agent.

Handles cart and order-related user requests: view cart contents, modify
cart, check availability, provide shipping and delivery information, and
assist with checkout workflows.
"""

from google.adk import Agent

from customer_service.config import Config
from customer_service.shared_libraries.callbacks import (
    after_tool,
    before_agent,
    before_tool,
    rate_limit_callback,
)
from customer_service.tools.order_management import (
    cancel_order,
    change_delivery_address,
    get_order_details,
    get_order_history,
    modify_order_list,
)

DESCRIPTION = "Manages and views orders: tracks shipments, cancels or modifies orders, checks delivery estimates."

INSTRUCTION = """
You are the Order Management sub-agent. Your job is to help customers with their orders: tracking shipments, modifying orders before they ship, cancelling orders, changing delivery addresses, and providing delivery estimates.

Always verify order IDs with the customer before making changes.
Inform customers about any fees or restrictions related to order modifications.
"""

TOOLS = [
    cancel_order,
    get_order_details,
    change_delivery_address,
    get_order_history,
    modify_order_list,
]


def create_agent(
    configs: Config | None = None, name: str | None = None, model: str | None = None
) -> Agent:
    """Create and return an ADK Agent configured for order management.

    Args:
        configs: Optional Config object used across the project. If omitted,
            a default Config() will be created.
        name: Optional agent name override.
        model: Optional model override string.

    Returns:
        google.adk.Agent: configured agent instance.
    """
    configs = configs or Config()
    agent_name = name or "order_management"
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

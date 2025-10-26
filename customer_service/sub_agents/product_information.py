"""Product information sub-agent.

Provides product details, identification assistance, recommendations, and
availability checks. Works closely with product recommendation tools and the
catalog/stock APIs (mocked in tools.py).
"""

from google.adk import Agent

from customer_service.config import Config
from customer_service.shared_libraries.callbacks import (
    after_tool,
    before_agent,
    before_tool,
    rate_limit_callback,
)
from customer_service.tools.product_information import (
    check_item_availability,
    check_product_availability,
    compare_products,
    get_product_details,
    get_product_specifications,
    search_products,
)

DESCRIPTION = "Provides product information: search products, check availability, and view specifications."

INSTRUCTION = """
You are the Product Information sub-agent. Your job is to help customers learn about products: searching the catalog, providing detailed specifications, and checking availability.

Be helpful and informative. Highlight key features and benefits.
When customers are unsure, ask clarifying questions about their needs.
Provide honest information from reviews, both positive and negative aspects.
"""

TOOLS = [
    search_products,
    get_product_details,
    compare_products,
    check_product_availability,
    get_product_specifications,
    check_item_availability,
]


def create_agent(
    configs: Config | None = None, name: str | None = None, model: str | None = None
) -> Agent:
    """Create and return an ADK Agent configured for product information.

    Args:
            configs: Optional Config object used across the project. If omitted,
                    a default Config() will be created.
            name: Optional agent name override.
            model: Optional model override string.

    Returns:
            google.adk.Agent: configured agent instance.
    """
    configs = configs or Config()
    agent_name = name or "product_information"
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

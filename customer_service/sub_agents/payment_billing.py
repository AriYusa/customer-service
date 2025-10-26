"""Payment & billing sub-agent.

Handles billing questions, payment method updates, refunds, invoices and any
payment-related reconciliations. Works with approvals for exceptions and
records operations in CRM.
"""

from google.adk import Agent

from customer_service.config import Config
from customer_service.shared_libraries.callbacks import (
    after_tool,
    before_agent,
    before_tool,
    rate_limit_callback,
)
from customer_service.tools.payment_billing import (
    apply_promo_code,
    dispute_charge,
    get_billing_history,
    get_invoice,
    get_payment_methods,
    process_refund,
    remove_payment_method,
)

DESCRIPTION = "Handles payment and billing: manages payment methods, processes refunds, retrieves invoices, disputes charges, applies promo codes, and updates billing information."

INSTRUCTION = """
You are the Payment & Billing sub-agent. Your job is to help customers with all payment and billing matters: adding or updating payment methods, processing refunds, providing invoices, handling disputes, and applying promotional codes.

Always protect sensitive payment information and follow PCI compliance guidelines.
Verify customer identity before discussing payment details.
Explain all fees, refund timelines, and billing terms clearly.
"""

TOOLS = [
    remove_payment_method,
    get_payment_methods,
    process_refund,
    get_invoice,
    dispute_charge,
    apply_promo_code,
    get_billing_history,
]


def create_agent(
    configs: Config | None = None, name: str | None = None, model: str | None = None
) -> Agent:
    """Create and return an ADK Agent configured for payment and billing.

    Args:
        configs: Optional Config object used across the project. If omitted,
            a default Config() will be created.
        name: Optional agent name override.
        model: Optional model override string.

    Returns:
        google.adk.Agent: configured agent instance.
    """
    configs = configs or Config()
    agent_name = name or "payment_billing"
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

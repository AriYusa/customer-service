"""Agent module for the customer service agent."""

import logging
import warnings

from google.adk import Agent
from langfuse import get_client
from openinference.instrumentation.google_adk import GoogleADKInstrumentor

from customer_service.database import database
from customer_service.sub_agents import (
    account_management,
    order_management,
    payment_billing,
    product_information,
    returns_refunds,
    technical_support,
)

from .config import Config
from .prompts import GLOBAL_INSTRUCTION, INSTRUCTION
from .shared_libraries.callbacks import (
    after_model,
    after_tool,
    before_agent,
    before_tool,
    rate_limit_callback,
)

warnings.filterwarnings("ignore", category=UserWarning, module=".*pydantic.*")

configs = Config()

# configure logging __name__
logger = logging.getLogger(__name__)

# Initialize the database
database.init_db()

langfuse = get_client()
# Verify connection
if langfuse.auth_check():
    print("Langfuse client is authenticated and ready!")
else:
    print("Authentication failed. Please check your credentials and host.")
GoogleADKInstrumentor().instrument()

account_management_agent = account_management.create_agent(configs)
order_management_agent = order_management.create_agent(configs)
payment_billing_agent = payment_billing.create_agent(configs)
product_information_agent = product_information.create_agent(configs)
returns_refunds_agent = returns_refunds.create_agent(configs)
technical_support_agent = technical_support.create_agent(configs)

root_agent = Agent(
    model=configs.agent_settings.model,
    global_instruction=GLOBAL_INSTRUCTION,
    description="Routing coordinator for customer service sub-agents. Has access to all sub-agent tools descriptions. Can assist with getting addifitional information by routing to the appropriate sub-agent.",
    instruction=INSTRUCTION,
    name=configs.agent_settings.name,
    sub_agents=[
        account_management_agent,
        order_management_agent,
        payment_billing_agent,
        product_information_agent,
        returns_refunds_agent,
        technical_support_agent,
    ],
    before_tool_callback=before_tool,
    after_tool_callback=after_tool,
    before_agent_callback=before_agent,
    before_model_callback=rate_limit_callback,
    after_model_callback=after_model,
)

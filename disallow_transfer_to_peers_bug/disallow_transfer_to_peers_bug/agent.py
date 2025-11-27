# pip install google-adk

import asyncio
import os
from google.adk.agents import LlmAgent
from google.genai import types
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

APP_NAME = "agents"
USER_ID = "user"
SESSION_ID = "session"
MODEL_NAME = "gemini-2.0-flash"

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"
os.environ["GOOGLE_API_KEY"] = ""  # Replace with actual API key

def get_recent_orders(date_str: str = '') -> list[dict]:
    """Fetch recent orders for the customer.
    Args:
        date_str: Optional date string to filter orders after this date.
    Returns:
        A list of recent orders with product names and prices."""
    return [
        {"product_name": "Shirt with embroidery, Size M", "price": 150},
    ]

# The sub-agent's instruction explicitly instructs to skip coordinator agent just for higher chance of reproducibility. 
# Without that instruction, the sub-agents still can call transfer_to_agent with sibling agent as argument, although disallow_transfer_to_peers=True is set.
def get_product_info(product_name: str) -> dict:
    """Fetch product information and care instructions for a given product.
   
     Args:
        product_name: The name of the product to fetch information for.
    Returns:
        A dictionary containing product information and care instructions."""
    return {"fabric": "Satin", "care_instructions": "Clean with a damp cloth. Avoid prolonged exposure to sunlight."}

order_management_agent = LlmAgent(name="order_management_agent",
                        model=MODEL_NAME,
                        instruction="Use the tools to fetch recent orders and customer information. " \
                        "Don't make up any information, only use the tools provided. " \
                        "If you can't handle the request, transfer directly to most suitable agent without asking the user." \
                        "To avoid unnecessary loops between agents and latency, transfer task to coordinator_agent only in extreme cases, when none of the sub-agents can handle the request.",
                        description="Fetches info about user orders and customer details.",
                        disallow_transfer_to_peers=True,
                        tools = [get_recent_orders])


products_info_agent = LlmAgent(name="products_info_agent",
                        model=MODEL_NAME,
                        instruction="Use the tool to fetch product information and care instructions for the specified products. " \
                        "Don't make up any information, only use the tools provided. " \
                        "If you can't handle the request, transfer directly to most suitable agent without asking the user." \
                        "To avoid unnecessary loops between agents and latency, transfer task to coordinator_agent only in extreme cases, when none of the sub-agents can handle the request.",
                        description="Provides product information and care instructions for the specified products (specify which products).",
                        disallow_transfer_to_peers=True,
                        tools = [get_product_info])

root_agent = LlmAgent(name="coordinator_agent", 
                    instruction="You are an agent that gathers information about user orders and product details by delegating tasks to sub-agents. Plan first and then delegate. Try to gather as much information as possible without asking the user for more details.",
                    model=MODEL_NAME,
                    sub_agents=[order_management_agent, products_info_agent])


# Agent Interaction
async def call_agent(runner, query):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    print(f"USER: {query}")
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content):
        if event.content and event.content.parts and event.content.parts[0].function_call:
            print(f"{event.author}: calls {event.content.parts[0].function_call.name} with args {event.content.parts[0].function_call.args}")
        if event.content and event.content.parts and event.content.parts[0].text:
            print(f"{event.author}: {event.content.parts[0].text}")
    print()


async def main():
    session_service = InMemorySessionService()
    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    await call_agent(runner, "Check my recent orders")

    await call_agent(runner, "Provide care instructions for it")

    await call_agent(runner, "What are my recent orders after 20/10/2025?")

if __name__ == "__main__":
    asyncio.run(main())

# output should be similar to this (see bug in third user query):
# USER: Check my recent orders
# Warning: there are non-text parts in the response: ['function_call'], returning concatenated text result from text parts. Check the full candidates.content.parts accessor to get the full model response.
# coordinator_agent: calls transfer_to_agent with args {'agent_name': 'order_management_agent'}
# order_management_agent: calls get_recent_orders with args {}
# order_management_agent: OK. I found one recent order: A Shirt with embroidery, Size M for $150.

# USER: Provide care instructions for it
# order_management_agent: I am sorry, I cannot provide care instructions as I only have access to order information. I do not have the ability to access product details like care instructions. I will transfer you to the coordinator agent who may be able to assist you further.

# coordinator_agent: calls transfer_to_agent with args {'agent_name': 'products_info_agent'}
# products_info_agent: calls get_product_info with args {'product_name': 'Shirt with embroidery, Size M'}
# products_info_agent: The care instructions for the Shirt with embroidery, Size M are: Clean with a damp cloth. Avoid prolonged exposure to sunlight. The fabric is Satin.

# USER: What are my recent orders after 20/10/2025?
# products_info_agent: calls transfer_to_agent with args {'agent_name': 'order_management_agent'} # !!! This is bug
# order_management_agent: calls get_recent_orders with args {'date_str': '20/10/2025'}
# order_management_agent: OK. I found one recent order after 20/10/2025: A Shirt with embroidery, Size M for $150.
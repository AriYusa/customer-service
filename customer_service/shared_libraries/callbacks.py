
"""Callback functions for FOMC Research Agent."""

import inspect
import logging
import time
from typing import Any, get_type_hints

from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.models import LlmRequest, LlmResponse
from google.adk.sessions.state import State
from google.adk.tools import BaseTool
from google.adk.tools.tool_context import ToolContext
from jsonschema import ValidationError
from pydantic import BaseModel

from customer_service.database.database import DEFAULT_CUSTOMER_ID
from customer_service.tools.account_management import (
    CustomerRecord,
    _get_customer_record,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

RATE_LIMIT_SECS = 60
RPM_QUOTA = 10


def rate_limit_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> None:
    """Callback function that implements a query rate limit.

    Args:
      callback_context: A CallbackContext obj representing the active callback
        context.
      llm_request: A LlmRequest obj representing the active LLM request.
    """
    for content in llm_request.contents:
        for part in content.parts:
            if part.text == "":
                part.text = " "

    now = time.time()
    if "timer_start" not in callback_context.state:
        callback_context.state["timer_start"] = now
        callback_context.state["request_count"] = 1
        logger.debug(
            "rate_limit_callback [timestamp: %i, req_count: 1, elapsed_secs: 0]",
            now,
        )
        return

    request_count = callback_context.state["request_count"] + 1
    elapsed_secs = now - callback_context.state["timer_start"]
    logger.debug(
        "rate_limit_callback [timestamp: %i, request_count: %i, elapsed_secs: %i]",
        now,
        request_count,
        elapsed_secs,
    )

    if request_count > RPM_QUOTA:
        delay = RATE_LIMIT_SECS - elapsed_secs + 1
        if delay > 0:
            logger.debug("Sleeping for %i seconds", delay)
            time.sleep(delay)
        callback_context.state["timer_start"] = now
        callback_context.state["request_count"] = 1
    else:
        callback_context.state["request_count"] = request_count

    return


def validate_customer_id(customer_id: str, session_state: State) -> tuple[bool, str]:
    """
    Validates the customer ID against the customer profile in the session state.

    Args:
        customer_id (str): The ID of the customer to validate.
        session_state (State): The session state containing the customer profile.

    Returns:
        A tuple containing an bool (True/False) and a String.
        When False, a string with the error message to pass to the model for deciding
        what actions to take to remediate.
    """
    if "customer_profile" not in session_state:
        return False, "No customer profile selected. Please select a profile."

    try:
        # We read the profile from the state, where it is set deterministically
        # at the beginning of the session.
        c = CustomerRecord.model_validate_json(session_state["customer_profile"])
        if customer_id == c.id:
            return True, None
        else:
            return (
                False,
                "You cannot use the tool with customer_id "
                + customer_id
                + ", only for "
                + c.id
                + ".",
            )
    except ValidationError:
        return (
            False,
            "Customer profile couldn't be parsed. Please reload the customer data. ",
        )


def lowercase_value(value):
    """Make dictionary lowercase"""
    if isinstance(value, dict):
        return (dict(k, lowercase_value(v)) for k, v in value.items())
    elif isinstance(value, str):
        return value.lower()
    elif isinstance(value, (list, set, tuple)):
        tp = type(value)
        return tp(lowercase_value(i) for i in value)
    else:
        return value


def convert_args_to_pydantic(tool: BaseTool, args: dict[str, Any]) -> dict[str, Any]:
    """Convert dictionary arguments to Pydantic model instances where applicable.
    
    Args:
        tool: The tool being called
        args: The arguments passed by the model
        
    Returns:
        dict[str, Any]: Arguments with Pydantic models converted from dicts
    """
    try:
        # Get the underlying function from the tool
        func = tool.func if hasattr(tool, 'func') else None
        if func is None:
            return args
            
        # Get type hints for the function
        type_hints = get_type_hints(func)
        
        # Create a new args dict with converted values
        converted_args = {}
        for param_name, param_value in args.items():
            if param_name in type_hints:
                param_type = type_hints[param_name]
                
                # Check if the parameter type is a Pydantic model
                if (
                    isinstance(param_value, dict) 
                    and inspect.isclass(param_type) 
                    and issubclass(param_type, BaseModel)
                ):
                    try:
                        # Convert dict to Pydantic model instance
                        converted_args[param_name] = param_type(**param_value)
                        logger.debug(
                            f"Converted argument '{param_name}' to {param_type.__name__}"
                        )
                    except Exception as e:
                        logger.warning(
                            f"Failed to convert argument '{param_name}' to {param_type.__name__}: {e}"
                        )
                        converted_args[param_name] = param_value
                # Handle list of Pydantic models
                elif (
                    isinstance(param_value, list) 
                    and param_value
                    and hasattr(param_type, '__origin__')
                    and param_type.__origin__ is list
                ):
                    # Get the list item type
                    list_item_type = param_type.__args__[0] if hasattr(param_type, '__args__') else None
                    if (
                        list_item_type 
                        and inspect.isclass(list_item_type) 
                        and issubclass(list_item_type, BaseModel)
                    ):
                        try:
                            # Convert list of dicts to list of Pydantic model instances
                            converted_list = []
                            for item in param_value:
                                if isinstance(item, dict):
                                    converted_list.append(list_item_type(**item))
                                else:
                                    converted_list.append(item)
                            converted_args[param_name] = converted_list
                            logger.debug(
                                f"Converted list argument '{param_name}' to list of {list_item_type.__name__}"
                            )
                        except Exception as e:
                            logger.warning(
                                f"Failed to convert list argument '{param_name}' to list of {list_item_type.__name__}: {e}"
                            )
                            converted_args[param_name] = param_value
                    else:
                        converted_args[param_name] = param_value
                else:
                    converted_args[param_name] = param_value
            else:
                converted_args[param_name] = param_value
                
        return converted_args
    except Exception as e:
        logger.error(f"Error in convert_args_to_pydantic: {e}")
        return args


# Callback Methods
def before_tool(tool: BaseTool, args: dict[str, Any], tool_context: CallbackContext):
    # Convert any dict arguments to Pydantic model instances if the function expects them
    converted_args = convert_args_to_pydantic(tool, args)
    
    # Update args with converted values
    args.clear()
    args.update(converted_args)
    
    # i make sure all values that the agent is sending to tools are lowercase
    lowercase_value(args)

    # Several tools require customer_id as input. We don't want to rely
    # solely on the model picking the right customer id. We validate it.
    # Alternative: tools can fetch the customer_id from the state directly.
    if "customer_id" in args:
        valid, err = validate_customer_id(args["customer_id"], tool_context.state)
        if not valid:
            return err

    # Only for centralized agents: prevent sub-agents from transferring
    if (
        tool_context.agent_name != "customer_service_coordinator"
        and tool.name == "transfer_to_agent"
        and args.get("agent_name") != "customer_service_coordinator"
    ):
        logger.info(
            "Sub-agent trying to transfer to another sub-agent, not allowed. Redirecting to coordinator."
        )
        args["agent_name"] = "customer_service_coordinator"

    return None


def after_tool(
    tool: BaseTool, args: dict[str, Any], tool_context: ToolContext, tool_response: dict
) -> dict | None:
    #   # After approvals, we perform operations deterministically in the callback
    #   # to apply the discount in the cart.
    #   if tool.name == "sync_ask_for_approval":
    #     if tool_response['status'] == "approved":
    #         logger.debug("Applying discount to the cart")
    #         # Actually make changes to the cart

    #   if tool.name == "approve_discount":
    #     if tool_response['status'] == "ok":
    #         logger.debug("Applying discount to the cart")
    #         # Actually make changes to the cart

    return None


# checking that the customer profile is loaded as state.
def before_agent(callback_context: InvocationContext):
    # In a production agent, this is set as part of the
    # session creation for the agent.
    if "customer_profile" not in callback_context.state:
        callback_context.state["customer_profile"] = _get_customer_record(
            DEFAULT_CUSTOMER_ID
        ).model_dump_json()
        # logger.info(callback_context.state["customer_profile"])


def after_model(callback_context: CallbackContext, llm_response: LlmResponse) -> None:
    """Callback function that processes the LLM response after generation.

    Args:
      callback_context: A CallbackContext obj representing the active callback
        context.
      llm_response: A LlmResponse obj representing the active LLM response.
    """
    # Example: Log the LLM response for debugging purposes
    logger.debug("LLM Response: %s", llm_response)

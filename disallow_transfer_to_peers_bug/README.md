# Bug: disallow_transfer_to_peers Not Enforced

## Description
When using `LlmAgent` with `disallow_transfer_to_peers=True`, sub-agents are still able to transfer tasks directly to sibling agents using `transfer_to_agent`, even though such transfers should be disallowed. 

## Example
Given the following setup (see `agent.py`):
- `order_management_agent` and `products_info_agent` both have `disallow_transfer_to_peers=True`.
- The root `coordinator_agent` delegates to these sub-agents.

### Expected Behavior
If a sub-agent cannot handle a request, it should only transfer to the coordinator agent, not directly to a peer.

### Actual Behavior (Bug)
In the third user query, the `products_info_agent` directly transfers to `order_management_agent`, bypassing the coordinator, even though `disallow_transfer_to_peers=True`.

### Why This Happens
The `disallow_transfer_to_peers=True` flag only influences the prompt given to the agent, restricting the list of allowed transfer options presented in the prompt. However, each sub-agent has access to the full conversation history, including all previous transfers and agent names mentioned. As a result, a sub-agent can still infer the names of sibling agents from the history and explicitly call `transfer_to_agent` with a sibling's name, bypassing the intended restriction.


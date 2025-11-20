### Run Traditional Tests (Recommended for CI/CD)
```bash
# Run just the returns/refunds tests
pytest eval/test_eval.py::test_eval_returns_refunds -v

# Run all evaluation tests
pytest eval/test_eval.py -v
```

### Setup User Simulation Testing
```bash
# Step 1: Create evalset
adk eval_set create customer_service returns_refunds_evalset

# Step 2: Add scenarios
adk eval_set add_eval_case customer_service returns_refunds_evalset --scenarios_file eval/eval_data/returns_refunds_scenarios.json --session_input_file eval/eval_data/session_input.json

# Step 3: Run evaluation
adk eval customer_service --config_file_path eval/eval_data/returns_refunds_usersim_config.json returns_refunds_evalset --print_detailed_results
```
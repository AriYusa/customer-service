"""Unit tests for callback functions."""

import unittest
from unittest.mock import Mock

from customer_service.datamodels.account import AddressData, SubscriptionPreferences, OrderItem
from customer_service.shared_libraries.callbacks import convert_args_to_pydantic


class TestConvertArgsToPydantic(unittest.TestCase):
    """Test cases for convert_args_to_pydantic function."""

    def test_convert_single_pydantic_model(self):
        """Test converting a dict to a single Pydantic model."""
        # Mock tool with a function that expects AddressData
        def mock_function(address_data: AddressData) -> bool:
            return True
        
        mock_tool = Mock()
        mock_tool.func = mock_function
        
        # Input args with dict
        args = {
            "address_data": {
                "line1": "123 Main St",
                "line2": "Apt 4",
                "city": "Springfield",
                "state": "IL",
                "postal_code": "62701",
                "country": "USA"
            }
        }
        
        # Convert
        converted = convert_args_to_pydantic(mock_tool, args)
        
        # Verify conversion
        self.assertIsInstance(converted["address_data"], AddressData)
        self.assertEqual(converted["address_data"].line1, "123 Main St")
        self.assertEqual(converted["address_data"].city, "Springfield")

    def test_convert_list_of_pydantic_models(self):
        """Test converting a list of dicts to a list of Pydantic models."""
        # Mock tool with a function that expects list of OrderItem
        def mock_function(updated_items: list[OrderItem]) -> bool:
            return True
        
        mock_tool = Mock()
        mock_tool.func = mock_function
        
        # Input args with list of dicts
        args = {
            "updated_items": [
                {"product_id": "prod1", "quantity": 2},
                {"product_id": "prod2", "quantity": 1}
            ]
        }
        
        # Convert
        converted = convert_args_to_pydantic(mock_tool, args)
        
        # Verify conversion
        self.assertIsInstance(converted["updated_items"], list)
        self.assertEqual(len(converted["updated_items"]), 2)
        self.assertIsInstance(converted["updated_items"][0], OrderItem)
        self.assertEqual(converted["updated_items"][0].product_id, "prod1")
        self.assertEqual(converted["updated_items"][0].quantity, 2)

    def test_mixed_arguments(self):
        """Test with mixed argument types (Pydantic and regular)."""
        # Mock tool with mixed parameters
        def mock_function(
            customer_id: str, 
            preferences: SubscriptionPreferences
        ) -> bool:
            return True
        
        mock_tool = Mock()
        mock_tool.func = mock_function
        
        # Input args with mixed types
        args = {
            "customer_id": "cust123",
            "preferences": {
                "marketing": True,
                "newsletters": False,
                "product_updates": True
            }
        }
        
        # Convert
        converted = convert_args_to_pydantic(mock_tool, args)
        
        # Verify conversion
        self.assertEqual(converted["customer_id"], "cust123")
        self.assertIsInstance(converted["preferences"], SubscriptionPreferences)
        self.assertTrue(converted["preferences"].marketing)
        self.assertFalse(converted["preferences"].newsletters)

    def test_no_conversion_needed(self):
        """Test when no conversion is needed."""
        # Mock tool with no Pydantic parameters
        def mock_function(customer_id: str, amount: float) -> bool:
            return True
        
        mock_tool = Mock()
        mock_tool.func = mock_function
        
        # Input args with no Pydantic types
        args = {
            "customer_id": "cust123",
            "amount": 99.99
        }
        
        # Convert
        converted = convert_args_to_pydantic(mock_tool, args)
        
        # Verify no conversion
        self.assertEqual(converted, args)
        self.assertEqual(converted["customer_id"], "cust123")
        self.assertEqual(converted["amount"], 99.99)

    def test_invalid_pydantic_data(self):
        """Test handling of invalid Pydantic data."""
        # Mock tool with a function that expects AddressData
        def mock_function(address_data: AddressData) -> bool:
            return True
        
        mock_tool = Mock()
        mock_tool.func = mock_function
        
        # Input args with invalid data (missing required field)
        args = {
            "address_data": {
                "line2": "Apt 4",
                "city": "Springfield"
                # Missing required 'line1' and 'postal_code'
            }
        }
        
        # Convert - should not raise exception, just log warning
        converted = convert_args_to_pydantic(mock_tool, args)
        
        # Verify original dict is returned on failure
        self.assertIsInstance(converted["address_data"], dict)

    def test_tool_without_func_attribute(self):
        """Test handling of tool without func attribute."""
        mock_tool = Mock(spec=[])  # No func attribute
        
        args = {"some_arg": "value"}
        
        # Convert - should return original args
        converted = convert_args_to_pydantic(mock_tool, args)
        
        self.assertEqual(converted, args)


if __name__ == "__main__":
    unittest.main()

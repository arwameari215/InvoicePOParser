"""
ERPNext Test Fixtures

Provides reusable test data for ERPNext integration tests.
These fixtures represent realistic entities that can be created/used in tests.
"""

from typing import Dict, Any
from datetime import datetime, timedelta


class ERPNextFixtures:
    """Centralized test fixtures for ERPNext entities."""
    
    # ========================================================================
    # Company Fixtures
    # ========================================================================
    
    @staticmethod
    def get_test_company() -> Dict[str, Any]:
        """
        Get test company data.
        
        Returns:
            Dict with company details
        """
        return {
            "doctype": "Company",
            "company_name": "Test Company CI",
            "abbr": "TCI",
            "default_currency": "USD",
            "country": "United States"
        }
    
    @staticmethod
    def get_company_update_data() -> Dict[str, Any]:
        """Get data for updating a company."""
        return {
            "phone_no": "+1-555-0100",
            "email": "info@testcompany.com"
        }
    
    # ========================================================================
    # Supplier Fixtures
    # ========================================================================
    
    @staticmethod
    def get_test_supplier(suffix: str = "") -> Dict[str, Any]:
        """
        Get test supplier data.
        
        Args:
            suffix: Optional suffix to make supplier name unique
        
        Returns:
            Dict with supplier details
        """
        name = f"Test Supplier{suffix}"
        return {
            "doctype": "Supplier",
            "supplier_name": name,
            "supplier_group": "All Supplier Groups",
            "supplier_type": "Company"
        }
    
    @staticmethod
    def get_supplier_list() -> list:
        """Get list of test suppliers for bulk operations."""
        return [
            ERPNextFixtures.get_test_supplier(" A"),
            ERPNextFixtures.get_test_supplier(" B"),
            ERPNextFixtures.get_test_supplier(" C")
        ]
    
    # ========================================================================
    # Customer Fixtures
    # ========================================================================
    
    @staticmethod
    def get_test_customer(suffix: str = "") -> Dict[str, Any]:
        """
        Get test customer data.
        
        Args:
            suffix: Optional suffix to make customer name unique
        
        Returns:
            Dict with customer details
        """
        name = f"Test Customer{suffix}"
        return {
            "doctype": "Customer",
            "customer_name": name,
            "customer_type": "Company",
            "customer_group": "All Customer Groups",
            "territory": "All Territories"
        }
    
    @staticmethod
    def get_customer_list() -> list:
        """Get list of test customers for bulk operations."""
        return [
            ERPNextFixtures.get_test_customer(" A"),
            ERPNextFixtures.get_test_customer(" B"),
            ERPNextFixtures.get_test_customer(" C")
        ]
    
    # ========================================================================
    # Item Fixtures
    # ========================================================================
    
    @staticmethod
    def get_test_item(suffix: str = "") -> Dict[str, Any]:
        """
        Get test item data.
        
        Args:
            suffix: Optional suffix to make item code unique
        
        Returns:
            Dict with item details
        """
        code = f"TEST-ITEM{suffix}"
        return {
            "doctype": "Item",
            "item_code": code,
            "item_name": f"Test Item{suffix}",
            "item_group": "All Item Groups",
            "stock_uom": "Nos",
            "is_stock_item": 0,
            "is_sales_item": 1,
            "is_purchase_item": 1
        }
    
    @staticmethod
    def get_item_list() -> list:
        """Get list of test items for bulk operations."""
        return [
            ERPNextFixtures.get_test_item("-001"),
            ERPNextFixtures.get_test_item("-002"),
            ERPNextFixtures.get_test_item("-003")
        ]
    
    # ========================================================================
    # Purchase Order Fixtures
    # ========================================================================
    
    @staticmethod
    def get_test_purchase_order_data(
        company: str = "Test Company CI",
        supplier: str = "Test Supplier",
        item_code: str = "TEST-ITEM-001"
    ) -> Dict[str, Any]:
        """
        Get complete purchase order data for workflow testing.
        
        Args:
            company: Company name
            supplier: Supplier name
            item_code: Item code for line item
        
        Returns:
            Dict with PO data matching workflow input format
        """
        today = datetime.now().strftime("%Y-%m-%d")
        delivery_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        return {
            "company_name": company,
            "supplier_name": supplier,
            "date": today,
            "delivery_date": delivery_date,
            "currency": "USD",
            "items": [
                {
                    "item_code": item_code,
                    "item_name": "Test Item 001",
                    "qty": 10,
                    "rate": 100.0,
                    "amount": 1000.0
                }
            ]
        }
    
    @staticmethod
    def get_test_po_with_multiple_items(
        company: str = "Test Company CI",
        supplier: str = "Test Supplier"
    ) -> Dict[str, Any]:
        """Get PO data with multiple line items."""
        today = datetime.now().strftime("%Y-%m-%d")
        delivery_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        return {
            "company_name": company,
            "supplier_name": supplier,
            "date": today,
            "delivery_date": delivery_date,
            "currency": "USD",
            "items": [
                {
                    "item_code": "TEST-ITEM-001",
                    "item_name": "Test Item 001",
                    "qty": 10,
                    "rate": 100.0,
                    "amount": 1000.0
                },
                {
                    "item_code": "TEST-ITEM-002",
                    "item_name": "Test Item 002",
                    "qty": 5,
                    "rate": 200.0,
                    "amount": 1000.0
                }
            ]
        }
    
    # ========================================================================
    # Sales Invoice Fixtures
    # ========================================================================
    
    @staticmethod
    def get_test_sales_invoice_data(
        company: str = "Test Company CI",
        customer: str = "Test Customer",
        item_code: str = "TEST-ITEM-001"
    ) -> Dict[str, Any]:
        """
        Get complete sales invoice data for workflow testing.
        
        Args:
            company: Company name
            customer: Customer name
            item_code: Item code for line item
        
        Returns:
            Dict with sales invoice data matching workflow input format
        """
        today = datetime.now().strftime("%Y-%m-%d")
        due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        return {
            "company_name": company,
            "customer_name": customer,
            "posting_date": today,
            "due_date": due_date,
            "currency": "USD",
            "items": [
                {
                    "item_code": item_code,
                    "description": "Test Item 001",
                    "qty": 5,
                    "rate": 150.0
                }
            ]
        }
    
    @staticmethod
    def get_test_invoice_with_multiple_items(
        company: str = "Test Company CI",
        customer: str = "Test Customer"
    ) -> Dict[str, Any]:
        """Get sales invoice data with multiple line items."""
        today = datetime.now().strftime("%Y-%m-%d")
        due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        return {
            "company_name": company,
            "customer_name": customer,
            "posting_date": today,
            "due_date": due_date,
            "currency": "USD",
            "items": [
                {
                    "item_code": "TEST-ITEM-001",
                    "description": "Test Item 001",
                    "qty": 5,
                    "rate": 150.0
                },
                {
                    "item_code": "TEST-ITEM-002",
                    "description": "Test Item 002",
                    "qty": 3,
                    "rate": 250.0
                },
                {
                    "item_code": "TEST-ITEM-003",
                    "description": "Test Item 003",
                    "qty": 2,
                    "rate": 500.0
                }
            ]
        }
    
    # ========================================================================
    # Invalid Data Fixtures (for error testing)
    # ========================================================================
    
    @staticmethod
    def get_invalid_po_missing_company() -> Dict[str, Any]:
        """Get invalid PO data (missing company)."""
        return {
            "supplier_name": "Test Supplier",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "items": []
        }
    
    @staticmethod
    def get_invalid_po_missing_supplier() -> Dict[str, Any]:
        """Get invalid PO data (missing supplier)."""
        return {
            "company_name": "Test Company CI",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "items": []
        }
    
    @staticmethod
    def get_invalid_invoice_missing_customer() -> Dict[str, Any]:
        """Get invalid invoice data (missing customer)."""
        return {
            "company_name": "Test Company CI",
            "posting_date": datetime.now().strftime("%Y-%m-%d"),
            "items": []
        }
    
    @staticmethod
    def get_invalid_currency_po() -> Dict[str, Any]:
        """Get PO with invalid/unsupported currency."""
        return {
            "company_name": "Test Company CI",
            "supplier_name": "Test Supplier",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "delivery_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "currency": "XYZ",  # Invalid currency
            "items": [
                {
                    "item_code": "TEST-ITEM-001",
                    "qty": 1,
                    "rate": 100.0
                }
            ]
        }

#!/usr/bin/env python
"""
Quick verification script to test the new testing infrastructure.
Run this to verify everything is set up correctly.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_fixtures():
    """Test that fixtures can be imported and used."""
    print("✓ Testing fixtures...")
    from tests.fixtures.erpnext_fixtures import ERPNextFixtures
    
    fixtures = ERPNextFixtures()
    company = fixtures.get_test_company()
    supplier = fixtures.get_test_supplier()
    po_data = fixtures.get_test_purchase_order_data()
    
    assert 'company_name' in company
    assert 'supplier_name' in supplier
    assert 'items' in po_data
    
    print("  ✅ Fixtures working correctly")
    return True

def test_erpnext_service():
    """Test that ERPNext service can be imported."""
    print("✓ Testing ERPNext service...")
    from app.services.erpnext_service import (
        test_connection,
        get_entity,
        ERPNextAPIError,
        ValidationError
    )
    
    print("  ✅ ERPNext service imports successfully")
    return True

def test_erpnext_config():
    """Test that ERPNext config can be loaded."""
    print("✓ Testing ERPNext config...")
    from app.config.erpnext_config import erpnext_config
    
    is_configured = erpnext_config.is_configured()
    print(f"  ℹ️  ERPNext configured: {is_configured}")
    
    if is_configured:
        print(f"  ℹ️  ERPNext URL: {erpnext_config.url}")
        print("  ✅ ERPNext configuration loaded")
    else:
        print("  ⚠️  ERPNext not configured (expected if .env missing)")
        print("     ERPNext integration tests will skip")
    
    return True

def test_workflows():
    """Test that workflows can be imported."""
    print("✓ Testing workflows...")
    from app.workflows.erpnext_workflows import (
        submit_purchase_order_workflow,
        submit_sales_invoice_workflow
    )
    
    print("  ✅ Workflows import successfully")
    return True

def main():
    """Run all verification tests."""
    print("=" * 60)
    print("Testing Infrastructure Verification")
    print("=" * 60)
    print()
    
    tests = [
        ("Fixtures", test_fixtures),
        ("ERPNext Service", test_erpnext_service),
        ("ERPNext Config", test_erpnext_config),
        ("Workflows", test_workflows),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
            print()
        except Exception as e:
            print(f"  ❌ {name} failed: {str(e)}")
            failed += 1
            print()
    
    print("=" * 60)
    print(f"Verification Results: {passed} passed, {failed} failed")
    print("=" * 60)
    print()
    
    if failed == 0:
        print("✅ All verification tests passed!")
        print()
        print("Next steps:")
        print("  1. Run unit tests:")
        print("     python -m unittest discover -s tests/unit -v")
        print()
        print("  2. Run API tests (mocked):")
        print("     python -m unittest discover -s tests/integration -p 'test_api*.py' -v")
        print()
        print("  3. Configure ERPNext (optional):")
        print("     cp .env.example .env")
        print("     # Edit .env with your ERPNext credentials")
        print()
        print("  4. Run ERPNext tests (requires .env):")
        print("     python -m unittest discover -s tests/integration -p 'test_erpnext*.py' -v")
        print()
        print("  5. Read full documentation:")
        print("     See TESTING_GUIDE.md for complete instructions")
        print()
        return 0
    else:
        print("❌ Some verification tests failed")
        print("   Check error messages above and fix issues")
        return 1

if __name__ == '__main__':
    sys.exit(main())

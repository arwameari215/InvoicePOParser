"""
Test script for Claude AI parsers.

This script tests the Claude integration without needing the full API server.
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.services.claude_service import ClaudeService
from app.parsers.invoice_claude_parser import InvoiceClaudeParser
from app.parsers.po_claude_parser import PurchaseOrderClaudeParser


def test_invoice_parser(pdf_path: str):
    """Test invoice parsing with Claude."""
    print("=" * 60)
    print("Testing Invoice Parser with Claude AI")
    print("=" * 60)
    print(f"PDF: {pdf_path}")
    print()
    
    try:
        # Initialize service
        print("1. Initializing Claude service...")
        service = ClaudeService(".anthropickey")
        print("✅ Claude service initialized")
        print()
        
        # Create parser
        print("2. Creating invoice parser...")
        parser = InvoiceClaudeParser(pdf_path, service)
        print("✅ Parser created")
        print()
        
        # Parse document
        print("3. Parsing invoice with Claude AI...")
        result = parser.parse()
        print("✅ Parsing complete")
        print()
        
        # Display results
        print("=" * 60)
        print("EXTRACTED DATA (Dictionary)")
        print("=" * 60)
        for key, value in result.items():
            print(f"{key:20} : {value}")
        print()
        
        # Display YAML
        print("=" * 60)
        print("YAML OUTPUT")
        print("=" * 60)
        yaml_output = parser.to_yaml()
        print(yaml_output)
        
        return result
    
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Make sure:")
        print("  1. PDF file exists at the specified path")
        print("  2. .anthropickey file exists in project root")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


def test_po_parser(pdf_path: str):
    """Test PO parsing with Claude."""
    print("=" * 60)
    print("Testing Purchase Order Parser with Claude AI")
    print("=" * 60)
    print(f"PDF: {pdf_path}")
    print()
    
    try:
        # Initialize service
        print("1. Initializing Claude service...")
        service = ClaudeService(".anthropickey")
        print("✅ Claude service initialized")
        print()
        
        # Create parser
        print("2. Creating PO parser...")
        parser = PurchaseOrderClaudeParser(pdf_path, service)
        print("✅ Parser created")
        print()
        
        # Parse document
        print("3. Parsing PO with Claude AI...")
        result = parser.parse()
        print("✅ Parsing complete")
        print()
        
        # Display results
        print("=" * 60)
        print("EXTRACTED DATA (Dictionary)")
        print("=" * 60)
        for key, value in result.items():
            if key == "items":
                print(f"{key:20} : [{len(value)} items]")
                for idx, item in enumerate(value, 1):
                    print(f"  Item {idx}:")
                    for k, v in item.items():
                        print(f"    {k:15} : {v}")
            else:
                print(f"{key:20} : {value}")
        print()
        
        # Display YAML
        print("=" * 60)
        print("YAML OUTPUT")
        print("=" * 60)
        yaml_output = parser.to_yaml()
        print(yaml_output)
        
        return result
    
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Make sure:")
        print("  1. PDF file exists at the specified path")
        print("  2. .anthropickey file exists in project root")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print()
    print("╔" + "=" * 58 + "╗")
    print("║  DocIntelligenceAPI - Claude AI Parser Test            ║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python test_claude_parsers.py invoice <path-to-invoice.pdf>")
        print("  python test_claude_parsers.py po <path-to-po.pdf>")
        print()
        print("Example:")
        print("  python test_claude_parsers.py invoice test_invoice.pdf")
        print("  python test_claude_parsers.py po test_po.pdf")
        sys.exit(1)
    
    doc_type = sys.argv[1].lower()
    pdf_path = sys.argv[2]
    
    if not os.path.exists(pdf_path):
        print(f"❌ Error: PDF file not found: {pdf_path}")
        sys.exit(1)
    
    if doc_type == "invoice":
        test_invoice_parser(pdf_path)
    elif doc_type in ["po", "purchase_order"]:
        test_po_parser(pdf_path)
    else:
        print(f"❌ Error: Unknown document type: {doc_type}")
        print("Supported types: invoice, po")
        sys.exit(1)

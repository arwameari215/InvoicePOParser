# Test Documentation

**Version**: 3.0.0  
**Last Updated**: 2026-01-29  
**Total Tests**: 108

---

## Overview

The test suite is organized into three main categories:

```
tests/
├── api/                              # API endpoint tests (51 tests)
│   ├── test_health.py               # Health/root endpoints
│   ├── clients/                     # API client helpers
│   ├── documents/                   # Document upload tests
│   └── erpnext/                     # ERPNext API tests (mocked)
│
├── core/                            # Business logic tests (32 tests)
│   └── parsers/
│       ├── test_parser_factory.py
│       ├── test_invoice_parser.py
│       └── test_po_parser.py
│
├── integration/                     # Integration tests (21 tests)
│   ├── erpnext/                     # Real ERPNext tests (NO MOCKS)
│   ├── workflows/                   # E2E workflows
│   └── helpers/                     # Shared test utilities
│
├── data/                            # Temporary test files (auto-created)
└── test_api.py                      # Legacy API tests (4 tests)
```

---

## Test Categories

### API Tests (51) - `tests/api/`
- **Health API**: 8 tests for `/`, `/health`, `/supported-types`
- **Document Upload**: 20 tests for invoice/PO uploads
- **ERPNext API (mocked)**: 16 tests with mocked services
- **Speed**: Fast (~10s), all dependencies mocked

### Core Tests (32) - `tests/core/`
- **Parser Factory**: 9 tests for document routing
- **Invoice Parser**: 15 tests for validation & normalization
- **PO Parser**: 13 tests for field cleaning & validation
- **Speed**: Very Fast (~1s), zero external dependencies

### Integration Tests (21) - `tests/integration/`
- **ERPNext Real**: 13 tests with actual CRUD operations (**NO MOCKS**)
- **Workflows**: 8 tests for end-to-end flows
- **Speed**: Slow (~30s), requires ERPNext
- **Auto-skips** if ERPNext unavailable

---

## Running Tests

### All Tests
```bash
# All 108 tests
venv/Scripts/python.exe -m unittest discover -s tests -p "test_*.py" -v
```

### By Category
```bash
# API tests (51)
venv/Scripts/python.exe -m unittest discover -s tests/api -p "test_*.py" -v

# Core tests (32)
venv/Scripts/python.exe -m unittest discover -s tests/core -p "test_*.py" -v

# Integration tests (21, requires ERPNext)
venv/Scripts/python.exe -m unittest discover -s tests/integration -p "test_*.py" -v

# Fast tests only (API + Core = 83 tests)
venv/Scripts/python.exe -m unittest discover -s tests/api -p "test_*.py"
venv/Scripts/python.exe -m unittest discover -s tests/core -p "test_*.py"
```

### Specific Files
```bash
# Parser tests
venv/Scripts/python.exe -m unittest tests.core.parsers.test_invoice_parser -v
venv/Scripts/python.exe -m unittest tests.core.parsers.test_po_parser -v

# API tests
venv/Scripts/python.exe -m unittest tests.api.test_health -v
venv/Scripts/python.exe -m unittest tests.api.documents.test_invoice_upload -v

# ERPNext tests
venv/Scripts/python.exe -m unittest tests.integration.erpnext.test_erpnext_real -v
venv/Scripts/python.exe -m unittest tests.integration.workflows.test_erpnext_workflows -v
```

---

## Environment Setup

### Core & API Tests
**None required** - All dependencies mocked

### ERPNext Integration Tests
Create `.env` file:
```bash
ERPNEXT_API_URL=https://your-erpnext-instance.com
ERPNEXT_API_KEY=your_api_key
ERPNEXT_API_SECRET=your_api_secret
```

ERPNext tests auto-skip if credentials not configured.

---

## Test Helpers

### Mock Helpers
```python
from tests.integration.helpers.mock_helpers import MockClaudeResponseBuilder

# Get mock data
invoice = MockClaudeResponseBuilder.perfect_invoice_response()
po = MockClaudeResponseBuilder.po_with_prefix_in_names()
```

### ERPNext Fixtures
```python
from tests.integration.helpers.erpnext_fixtures import ERPNextFixtures

# Get test data
company = ERPNextFixtures.get_test_company()
supplier = ERPNextFixtures.get_test_supplier()
```

### Base Test Case
```python
from tests.integration.helpers.base_test_case import BaseTestCase

class MyTest(BaseTestCase):
    def test_example(self):
        self.assertValidISO8601Date("2024-01-15")
        self.assertValidCurrencyCode("USD")
```

---

## CI/CD Integration

### GitHub Actions
```yaml
# Fast tests (always run)
- name: Run Core & API Tests
  run: |
    python -m unittest discover -s tests/api -p "test_*.py" -v
    python -m unittest discover -s tests/core -p "test_*.py" -v

# ERPNext tests (optional, non-blocking)
- name: Run ERPNext Tests
  continue-on-error: true
  env:
    ERPNEXT_API_URL: ${{ secrets.ERPNEXT_API_URL }}
    ERPNEXT_API_KEY: ${{ secrets.ERPNEXT_API_KEY }}
    ERPNEXT_API_SECRET: ${{ secrets.ERPNEXT_API_SECRET }}
  run: |
    python -m unittest discover -s tests/integration -p "test_*.py" -v
```

---

## Troubleshooting

### Import Errors
```bash
# Ensure you're in project root
cd InvoicePOParser

# Activate virtual environment
venv/Scripts/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### ERPNext Tests Skipped
```bash
# Verify .env file
cat .env

# Test connection
curl -X GET "https://your-erpnext.com/api/resource/Company" \
  -H "Authorization: token api_key:api_secret"
```

### Import Path Updates
After reorganization, use new import paths:
```python
# Old (DON'T USE)
from tests.base.base_test_case import BaseTestCase
from tests.fixtures.erpnext_fixtures import ERPNextFixtures

# New (USE THESE)
from tests.integration.helpers.base_test_case import BaseTestCase
from tests.integration.helpers.erpnext_fixtures import ERPNextFixtures
```

---

## Quick Reference

| Category | Location | Tests | Speed | Dependencies |
|----------|----------|-------|-------|--------------|
| **API** | `tests/api/` | 51 | Fast | None (mocked) |
| **Core** | `tests/core/` | 32 | Very Fast | None |
| **Integration** | `tests/integration/` | 21 | Slow | ERPNext (optional) |
| **TOTAL** | | **108** | ~31s | |

### Common Commands
```bash
# All tests
venv/Scripts/python.exe -m unittest discover -s tests -p "test_*.py" -v

# Fast only (no ERPNext)
venv/Scripts/python.exe -m unittest discover -s tests/api -p "test_*.py"
venv/Scripts/python.exe -m unittest discover -s tests/core -p "test_*.py"

# Specific category
venv/Scripts/python.exe -m unittest discover -s tests/api -p "test_*.py" -v
venv/Scripts/python.exe -m unittest discover -s tests/core -p "test_*.py" -v
venv/Scripts/python.exe -m unittest discover -s tests/integration -p "test_*.py" -v
```

---

**Need Help?** Run tests with `-v` flag for detailed output.


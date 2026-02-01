# Testing Guide

Comprehensive guide for running backend tests with ERPNext integration.

## Table of Contents

1. [Test Structure](#test-structure)
2. [Running Tests Locally](#running-tests-locally)
3. [ERPNext Integration Tests](#erpnext-integration-tests)
4. [CI/CD Testing](#cicd-testing)
5. [Test Coverage](#test-coverage)
6. [Troubleshooting](#troubleshooting)

---

## Test Structure

The test suite is organized into three main categories:

```
tests/
├── fixtures/
│   ├── erpnext_fixtures.py      # Test data for ERPNext entities
│   └── __init__.py
├── unit/                         # Unit tests (isolated, fast)
│   ├── test_invoice_parser.py
│   ├── test_po_parser.py
│   └── test_parser_factory.py
├── integration/                  # Integration tests
│   ├── api_clients/              # API test utilities
│   ├── test_api_health.py        # API health checks (mocked)
│   ├── test_api_invoice_upload.py  # Invoice upload tests (mocked)
│   ├── test_api_po_upload.py     # PO upload tests (mocked)
│   ├── test_erpnext_api.py       # ERPNext API tests (mocked)
│   ├── test_erpnext_real.py      # Real ERPNext connection tests
│   └── test_erpnext_workflows.py # Real ERPNext workflow tests
└── base/                         # Test utilities and helpers
    ├── base_test_case.py
    └── mock_helpers.py
```

### Test Categories

1. **Unit Tests** (`tests/unit/`)
   - Test individual components in isolation
   - Use mocks for all external dependencies
   - Fast execution, no network calls
   - Run in all environments (local, CI)

2. **API Tests** (`tests/integration/test_api_*.py`)
   - Test API endpoints with mocked services
   - Validate request/response structure
   - Test error handling
   - Run in all environments

3. **ERPNext Integration Tests** (`tests/integration/test_erpnext_*.py`)
   - **Real ERPNext Connection** - NO MOCKS
   - Test actual ERPNext API operations
   - Validate data creation and retrieval
   - Skip automatically if ERPNext unavailable

---

## Running Tests Locally

### Prerequisites

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create API key file (for document parsing tests)
echo "sk-ant-api03-your-key-here" > .anthropickey

# 3. For ERPNext tests: Configure .env file (optional)
cp .env.example .env
# Edit .env with your ERPNext credentials
```

### Run All Tests

```bash
# Run all tests (unit, API, and ERPNext if configured)
python -m unittest discover -s tests -p "test_*.py" -v
```

### Run Specific Test Suites

```bash
# Unit tests only (fast, no external dependencies)
python -m unittest discover -s tests/unit -p "test_*.py" -v

# API tests only (mocked, no ERPNext required)
python -m unittest discover -s tests/integration -p "test_api*.py" -v

# ERPNext integration tests only (requires real ERPNext)
python -m unittest discover -s tests/integration -p "test_erpnext*.py" -v
```

### Run Individual Test Files

```bash
# Run specific test file
python -m unittest tests.unit.test_invoice_parser -v

# Run specific test class
python -m unittest tests.unit.test_invoice_parser.TestInvoiceClaudeParser -v

# Run specific test method
python -m unittest tests.unit.test_invoice_parser.TestInvoiceClaudeParser.test_perfect_invoice_parsing -v
```

### Run with Coverage

```bash
# Install coverage tool
pip install coverage

# Run tests with coverage
coverage run -m unittest discover -s tests -p "test_*.py"

# Generate coverage report
coverage report

# Generate HTML coverage report
coverage html
# Open htmlcov/index.html in browser
```

---

## ERPNext Integration Tests

### Overview

ERPNext integration tests connect to a **REAL ERPNext instance** and perform actual operations:
- Create suppliers, customers, items
- Submit purchase orders and sales invoices
- Validate data retrieval and updates

**Important**: These tests use **NO MOCKS** - they test the real ERP client module.

### Setup ERPNext for Testing

#### Option 1: Local ERPNext Instance

```bash
# 1. Install ERPNext locally (recommended for development)
# Follow: https://github.com/frappe/bench

# 2. Configure .env file
ERPNEXT_URL=http://localhost:8080
ERPNEXT_API_KEY=your_api_key_here
ERPNEXT_API_SECRET=your_api_secret_here

# 3. Generate API credentials in ERPNext
# - Login to ERPNext
# - Go to: User → Your User → API Access
# - Click "Generate Keys"
# - Copy API Key and API Secret to .env
```

#### Option 2: ERPNext Cloud/Hosted Instance

```bash
# Use your hosted ERPNext instance
ERPNEXT_URL=https://yourcompany.erpnext.com
ERPNEXT_API_KEY=your_api_key
ERPNEXT_API_SECRET=your_api_secret
```

### Running ERPNext Tests

```bash
# 1. Ensure .env is configured
cat .env  # Should show ERPNEXT_* variables

# 2. Run ERPNext integration tests
python -m unittest tests.integration.test_erpnext_real -v
python -m unittest tests.integration.test_erpnext_workflows -v

# 3. Tests will automatically skip if ERPNext is unavailable
# Look for: "ERPNext not configured" or "ERPNext not reachable"
```

### Test Behavior

- **ERPNext Configured**: Tests create real entities and validate workflows
- **ERPNext Not Configured**: Tests skip automatically with informative messages
- **ERPNext Unreachable**: Tests skip with connection error details

Example output when skipped:
```
test_create_supplier (tests.integration.test_erpnext_real.TestERPNextEntityOperations) ... 
skipped 'ERPNext not configured (missing credentials in .env)'
```

### Test Data Cleanup

Test entities are prefixed with "Test" or "IntegTest" for easy identification:
- Suppliers: "Test Supplier IntegTest1", "Test Supplier IntegTest2"
- Customers: "Test Customer IntegTest1"
- Items: "TEST-ITEM-INTEG1", "TEST-ITEM-INTEG2"

**Manual Cleanup** (optional):
```bash
# In ERPNext, you can delete test entities:
# - Go to relevant DocType (Supplier, Customer, Item)
# - Filter by "Test" prefix
# - Bulk delete if desired
```

---

## CI/CD Testing

### GitHub Actions Workflow

The CI pipeline automatically runs tests on every push and pull request.

#### Test Execution in CI

1. **Unit Tests** (always run)
   - Fast, isolated tests
   - No external dependencies
   - Must pass for PR to be merged

2. **API Tests** (always run)
   - Test endpoints with mocks
   - Validate request/response structure
   - Must pass for PR to be merged

3. **ERPNext Integration Tests** (optional)
   - Run only if ERPNext credentials configured as secrets
   - Non-blocking (won't fail CI if skipped)
   - Useful for validating against staging ERPNext

#### Configure ERPNext in CI (Optional)

To enable ERPNext tests in GitHub Actions:

1. Go to: **Repository → Settings → Secrets and Variables → Actions**

2. Add repository secrets:
   ```
   ERPNEXT_URL=https://your-test-erpnext.com
   ERPNEXT_API_KEY=your_api_key
   ERPNEXT_API_SECRET=your_api_secret
   ```

3. Tests will automatically run against configured ERPNext instance

#### Viewing Test Results

```bash
# In GitHub Actions:
# 1. Go to "Actions" tab in repository
# 2. Click on workflow run
# 3. Expand test steps to see results

# Test sections:
# ✅ Run Unit and API Tests - Must pass
# ⚠️  Run ERPNext Integration Tests - May skip if not configured
```

### Test Artifacts

On test failure, CI uploads:
- **Server logs**: `server-logs-python-X.Y.tar.gz`
- Available for 7 days
- Download from "Artifacts" section in failed workflow run

---

## Test Coverage

### Current Test Coverage

```
Module                          Statements    Missing    Coverage
----------------------------------------------------------------
app/main.py                     45            2          95%
app/parser_factory.py           68            5          93%
app/parsers/invoice_parser.py   145           12         92%
app/parsers/po_parser.py        128           10         92%
app/services/claude_service.py  89            8          91%
app/services/erpnext_service.py 156           15         90%
app/workflows/erpnext_workflows.py  234       22         91%
----------------------------------------------------------------
TOTAL                           865           74         91%
```

### Measuring Coverage Locally

```bash
# Install coverage
pip install coverage

# Run with coverage
coverage run -m unittest discover -s tests -p "test_*.py"

# View report
coverage report

# Generate HTML report
coverage html
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

### Coverage Goals

- **Critical modules**: 90%+ (parsers, services, workflows)
- **API endpoints**: 85%+ (routers)
- **Utilities**: 80%+ (config, utils)

---

## Troubleshooting

### Common Issues

#### 1. Import Errors

```
ModuleNotFoundError: No module named 'app'
```

**Solution**:
```bash
# Ensure you're in project root
cd InvoicePOParser

# Run tests with Python module syntax
python -m unittest discover -s tests -p "test_*.py" -v
```

#### 2. ERPNext Tests Always Skip

```
skipped 'ERPNext not configured'
```

**Solution**:
```bash
# Check .env file exists and has correct format
cat .env

# Verify credentials
ERPNEXT_URL=http://localhost:8080    # No trailing slash
ERPNEXT_API_KEY=your_key
ERPNEXT_API_SECRET=your_secret

# Test connection manually
python -c "from app.services.erpnext_service import test_connection; print(test_connection())"
```

#### 3. API Key Not Found (Document Parser Tests)

```
FileNotFoundError: .anthropickey not found
```

**Solution**:
```bash
# Create API key file
echo "sk-ant-api03-your-actual-key-here" > .anthropickey

# Or use dummy key for tests that use mocks
echo "sk-ant-api03-dummy-key-for-testing" > .anthropickey
```

#### 4. Server Already Running (Port Conflict)

```
OSError: [Errno 48] Address already in use
```

**Solution**:
```bash
# Find and kill process on port 8000
# macOS/Linux:
lsof -ti:8000 | xargs kill -9

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

#### 5. Test Database/State Issues

```
ERPNextAPIError: Duplicate entry
```

**Solution**:
```bash
# ERPNext tests create entities with unique names
# If you see duplicates, entities weren't cleaned up

# Option 1: Use different test data
# Tests use timestamps or counters for uniqueness

# Option 2: Manually delete test entities in ERPNext
# Filter by "Test" prefix and delete
```

### Debug Mode

```bash
# Run tests with verbose output
python -m unittest discover -s tests -p "test_*.py" -v

# Run with Python debugging
python -m pdb -m unittest tests.integration.test_erpnext_real

# Enable logging
export LOG_LEVEL=DEBUG
python -m unittest discover -s tests -p "test_*.py" -v
```

### Getting Help

1. Check test output for specific error messages
2. Review test file docstrings for test requirements
3. Validate environment configuration (.env, .anthropickey)
4. Check server logs: `tail -f server.log` (if running server)
5. Run tests individually to isolate issues

---

## Best Practices

### Writing New Tests

1. **Use Fixtures**
   ```python
   from tests.fixtures.erpnext_fixtures import ERPNextFixtures
   
   def test_something(self):
       data = ERPNextFixtures.get_test_supplier()
       # Test with fixture data
   ```

2. **Mock External Services**
   ```python
   @patch('app.services.erpnext_service.requests.post')
   def test_api_call(self, mock_post):
       mock_post.return_value.json.return_value = {'success': True}
       # Test with mocked API
   ```

3. **Use Descriptive Test Names**
   ```python
   def test_create_supplier_with_valid_data_returns_success(self):
       """Test that creating supplier with valid data returns success response."""
       pass
   ```

4. **Skip Appropriately**
   ```python
   @skip_if_erpnext_unavailable
   def test_real_erpnext_operation(self):
       """Test with real ERPNext - skips if unavailable."""
       pass
   ```

5. **Clean Up Resources**
   ```python
   def tearDown(self):
       """Clean up test resources."""
       # Delete temporary files
       # Close connections
       pass
   ```

### Test Maintenance

- **Keep fixtures up to date** with ERPNext schema changes
- **Update mocks** when service interfaces change
- **Review skipped tests** periodically
- **Monitor test execution time** - keep unit tests fast
- **Update documentation** when adding new test categories

---

## Quick Reference

```bash
# Run all tests
python -m unittest discover -s tests -p "test_*.py" -v

# Run only unit tests (fast)
python -m unittest discover -s tests/unit -v

# Run only API tests (mocked, medium speed)
python -m unittest discover -s tests/integration -p "test_api*.py" -v

# Run only ERPNext tests (real connection, slow)
python -m unittest discover -s tests/integration -p "test_erpnext*.py" -v

# Run with coverage
coverage run -m unittest discover -s tests -p "test_*.py"
coverage report

# Run specific test
python -m unittest tests.integration.test_erpnext_real.TestERPNextConnection.test_connection_to_erpnext -v
```

---

## Summary

✅ **Unit tests**: Fast, isolated, always run
✅ **API tests**: Mocked, validate endpoints, always run  
✅ **ERPNext tests**: Real connection, skip if unavailable
✅ **CI pipeline**: Automated, runs on every push
✅ **Test fixtures**: Reusable test data
✅ **Documentation**: This guide!

**Ready to test!** 🚀

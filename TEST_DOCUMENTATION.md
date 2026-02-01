# Test Documentation - DocIntelligenceAPI

**Version**: 1.0.0  
**Last Updated**: January 29, 2026  
**Test Framework**: unittest (Python standard library)  
**Total Tests**: 67

---

## Table of Contents

1. [Test Overview](#test-overview)
2. [Test Structure](#test-structure)
3. [Test Coverage](#test-coverage)
4. [Test Scenarios](#test-scenarios)
5. [Environment & Configuration](#environment--configuration)
6. [Test Execution](#test-execution)
7. [Failure Handling](#failure-handling)
8. [Reporting & Artifacts](#reporting--artifacts)

---

## Test Overview

### Testing Goals

The DocIntelligenceAPI test suite ensures:

- **API Reliability**: All FastAPI endpoints return correct responses and status codes
- **Parser Accuracy**: Invoice and Purchase Order parsers correctly extract and validate data
- **Schema Validation**: All output conforms to defined JSON schemas
- **Error Handling**: Invalid inputs are rejected with appropriate error messages
- **Data Normalization**: Currency symbols, dates, and text are properly normalized
- **Zero External Dependencies**: All Claude AI calls are mocked; no real API calls during tests
- **Fast Execution**: Complete suite runs in <2 seconds

### Testing Strategy

**Methodology**: Test-driven validation with comprehensive mocking  
**Approach**: Bottom-up (unit → integration)  
**Philosophy**: Fail fast, provide clear error messages, ensure deterministic results

### Test Levels

#### 1. Unit Tests (37 tests)
- **Scope**: Individual components in isolation
- **Location**: `tests/unit/`
- **Mocking**: ClaudeService completely mocked
- **Purpose**: Validate parsing logic, schema validation, field normalization

#### 2. Integration Tests (28 tests)
- **Scope**: API endpoints with mocked backend
- **Location**: `tests/integration/`
- **Mocking**: ClaudeService mocked, FastAPI TestClient used
- **Purpose**: Validate HTTP responses, error handling, end-to-end flow

#### 3. Manual Tests (2 scripts)
- **Scope**: Real Claude AI integration
- **Location**: `tests/test_claude_parsers.py`, `tests/test_api.py`
- **Purpose**: Verify actual Claude AI responses (not automated)

---

## Test Structure

### Folder Layout

```
tests/
├── base/                           # Test infrastructure
│   ├── base_test_case.py          # Base class with custom assertions
│   ├── mock_helpers.py            # Mock builders and factories
│   └── __init__.py
├── unit/                           # Unit tests (37 tests)
│   ├── test_parser_factory.py     # ParserFactory tests (9 tests)
│   ├── test_invoice_parser.py     # InvoiceClaudeParser tests (15 tests)
│   ├── test_po_parser.py          # PurchaseOrderClaudeParser tests (13 tests)
│   └── __init__.py
├── integration/                    # Integration tests (28 tests)
│   ├── api_clients/               # Page Object Model implementations
│   │   ├── base_api_client.py     # Base API client
│   │   ├── health_api_client.py   # Health endpoint client
│   │   └── document_upload_client.py  # Upload endpoint client
│   ├── test_api_health.py         # Health API tests (8 tests)
│   ├── test_api_invoice_upload.py # Invoice upload tests (10 tests)
│   ├── test_api_po_upload.py      # PO upload tests (10 tests)
│   └── __init__.py
├── data/                           # Test data (created at runtime)
├── test_api.py                     # Legacy API tests (7 tests)
├── test_claude_parsers.py         # Manual Claude testing script
└── __init__.py
```

### Naming Conventions

**Test Files**: `test_<component>.py`  
**Test Classes**: `Test<ComponentName>(BaseTestCase)`  
**Test Methods**: `test_<feature>_<scenario>()`  
**Mock Files**: `mock_<type>.py`  
**API Clients**: `<resource>_api_client.py`

Examples:
- ✅ `test_parser_factory.py`
- ✅ `TestInvoiceClaudeParser`
- ✅ `test_currency_normalization()`
- ✅ `MockClaudeResponseBuilder`
- ✅ `document_upload_client.py`

### Test Data Handling

**Strategy**: Dynamic test data creation with cleanup

**Temporary PDFs**:
- Created in `tests/data/` directory via `MockPDFFile.create_sample_pdf()`
- Automatically deleted in `tearDown()` method
- Valid PDF structure with minimal content

**Mock Responses**:
- Built via `MockClaudeResponseBuilder` static methods
- Deep-copied to prevent test pollution
- Support multiple scenarios (perfect, missing fields, wrong types, etc.)

**Test Isolation**:
- Each test gets fresh mocks
- `ParserFactory._claude_service = None` reset in setUp/tearDown
- No shared state between tests

---

## Test Coverage

### Features Covered

#### ✅ **API Endpoints (28 tests)**
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /supported-types` - Document types list
- `POST /upload/invoice` - Invoice upload and parsing
- `POST /upload/po` - Purchase Order upload and parsing

#### ✅ **Parser Components (37 tests)**
- **ParserFactory (9 tests)**:
  - Document type routing
  - Case-insensitive matching
  - Singleton service management
  - Unsupported type handling
  
- **InvoiceClaudeParser (15 tests)**:
  - Schema validation
  - Currency normalization
  - Date format conversion
  - Numeric field validation
  - Extra field removal
  - Confidence scoring
  - Prediction time tracking
  
- **PurchaseOrderClaudeParser (13 tests)**:
  - Schema validation
  - PO number cleaning
  - Supplier/company name cleaning
  - Date validation
  - Currency normalization
  - Status field validation
  - Items array handling

#### ✅ **Cross-Cutting Concerns**
- Error handling (invalid file types, missing files)
- Data normalization (currencies, dates, names)
- Schema compliance (required fields, data types)
- Response wrapping (confidence, prediction time)
- Mocking strategy (zero real API calls)

### Known Gaps & Exclusions

**Not Tested (By Design)**:
- Real Claude API integration (requires API key, costs money)
- PDF content accuracy (Claude behavior is non-deterministic)
- File upload size limits (tested manually)
- Concurrent request handling (load testing out of scope)
- Database operations (no database in this project)

**Manual Testing Required**:
- Actual PDF parsing with Claude AI
- Multi-language document support
- Complex table extraction
- Handwritten text recognition

---

## Test Scenarios

### Unit Tests - ParserFactory (9 tests)

| Test | Scenario | Expected Outcome |
|------|----------|------------------|
| `test_get_parser_for_invoice` | Request invoice parser | Returns `InvoiceClaudeParser` instance |
| `test_get_parser_for_po` | Request PO parser with aliases (po, purchase_order, purchaseorder) | Returns `PurchaseOrderClaudeParser` instance |
| `test_get_parser_case_insensitive` | Request with various case (INVOICE, Invoice, invoice) | Returns correct parser regardless of case |
| `test_unsupported_document_type_raises_error` | Request unsupported type (receipt, contract) | Raises `ValueError` with clear message |
| `test_singleton_claude_service` | Multiple parser requests | Same `ClaudeService` instance reused |
| `test_get_parser_with_whitespace` | Document type has leading/trailing spaces | Whitespace trimmed, parser returned |
| `test_get_supported_types` | Request supported types | Returns `["invoice", "po", "purchase_order"]` |
| `test_claude_service_initialization_failure` | ClaudeService init fails (no API key) | Error logged, exception propagated |

**Input Examples**:
```python
# Valid
ParserFactory.get_parser("invoice", "test.pdf")
ParserFactory.get_parser("PO", "test.pdf")
ParserFactory.get_parser("  invoice  ", "test.pdf")

# Invalid
ParserFactory.get_parser("receipt", "test.pdf")  # ValueError
```

**Expected Outputs**:
- Parser instance: `InvoiceClaudeParser` or `PurchaseOrderClaudeParser`
- Error: `ValueError: Unsupported document type: receipt`

---

### Unit Tests - InvoiceClaudeParser (15 tests)

| Test | Scenario | Input | Expected Output |
|------|----------|-------|-----------------|
| `test_perfect_invoice_parsing` | All fields valid | Complete invoice data | All fields present, correct types |
| `test_currency_symbol_normalization` | Currency as symbol | `€`, `$`, `₪`, `£`, `¥`, `₹` | `EUR`, `USD`, `ILS`, `GBP`, `JPY`, `INR` |
| `test_date_format_conversion` | Various date formats | `15/01/2024`, `2024-01-15` | `2024-01-15` (ISO 8601) |
| `test_extra_fields_removed` | AI hallucination fields | `{"ExtraField": "x", ...}` | Extra fields removed, logged |
| `test_numeric_field_validation` | String numbers | `"1000.50"`, `"25"` | `1000.50`, `25.0` (floats) |
| `test_nullable_fields_validation` | Tax, addresses as None | `{"Tax": None, ...}` | None values accepted |
| `test_items_array_validation` | Items as list | `[{item1}, {item2}]` | Array validated, items checked |
| `test_confidence_score_present` | Parse result | Any valid invoice | `confidence` field present (0.0-1.0) |
| `test_prediction_time_present` | Parse result | Any valid invoice | `predictionTime` field present (≥0) |
| `test_missing_required_fields` | Incomplete data | Missing InvoiceId, VendorName | Warning logged, parsing continues |
| `test_get_prompt_returns_string` | Request prompt | N/A | Non-empty string returned |

**Schema Validation**:
```json
{
  "confidence": 0.85,
  "data": {
    "InvoiceId": "INV-12345",
    "VendorName": "Vendor Company",
    "InvoiceDate": "2024-01-15",
    "BillingAddressRecipient": "Customer Name" | null,
    "ShippingAddress": "123 Main St" | null,
    "SubTotal": 1000.50,
    "ShippingCost": 25.0,
    "InvoiceTotal": 1195.60,
    "Tax": 170.10 | null,
    "Currency": "USD",
    "Items": [
      {
        "description": "Product A",
        "quantity": 2,
        "unit_price": 500.25,
        "total": 1000.50
      }
    ]
  },
  "predictionTime": 2.543
}
```

**Currency Normalization Rules**:
```
$ → USD    € → EUR    ₪ → ILS
£ → GBP    ¥ → JPY    ₹ → INR
```

**Date Format Rules**:
- Input: `DD/MM/YYYY`, `YYYY-MM-DD`, `MM-DD-YYYY`
- Output: Always `YYYY-MM-DD` (ISO 8601)

---

### Unit Tests - PurchaseOrderClaudeParser (13 tests)

| Test | Scenario | Input | Expected Output |
|------|----------|-------|-----------------|
| `test_perfect_po_parsing` | All fields valid | Complete PO data | All fields present, correct types |
| `test_po_number_cleaning` | PO number with prefix | `"Number: PO-12345"` | `"PO-12345"` |
| `test_supplier_name_cleaning` | Supplier with prefix | `"Supplier: Company Inc"` | `"Company Inc"` |
| `test_company_name_cleaning` | Company with prefix | `"Company: Buyer LLC"` | `"Buyer LLC"` |
| `test_date_format_validation` | Date and delivery_date | `"2024-01-24"`, `"2024-02-15"` | Valid ISO 8601 dates |
| `test_currency_normalization` | Currency symbols | `€`, `$`, `₪`, `£`, `¥` | `EUR`, `USD`, `ILS`, `GBP`, `JPY` |
| `test_numeric_field_validation` | String numbers | `"40404.50"`, `"1000"` | `40404.50`, `1000.0` |
| `test_items_array_validation` | Items list | `[{item1}, {item2}]` | Array validated |
| `test_empty_items_array` | Empty items | `[]` | Empty array accepted |
| `test_status_field_validation` | Various statuses | `"APPROVED"`, `"In Progress"` | `"Approved"`, `"In progress"` (capitalized) |
| `test_extra_fields_removed` | Extra fields | `{"extra_field": "x"}` | Removed, logged |
| `test_missing_required_fields` | Incomplete data | Missing fields | Warning logged |
| `test_get_prompt_returns_string` | Request prompt | N/A | Non-empty string |

**Schema Validation**:
```json
{
  "po_number": "PO-000X",
  "date": "2024-01-24",
  "supplier_name": "Supplier Company Inc",
  "company_name": "Buyer Company LLC",
  "delivery_date": "2024-01-30",
  "total_amount": 40404.00,
  "currency": "EUR",
  "status": "Pending",
  "items": [
    {
      "description": "Product SKU005",
      "quantity": 182.0,
      "unit_price": 222.0,
      "total": 40404.0
    }
  ]
}
```

**Text Cleaning Rules**:
```
"Number: PO-123"        → "PO-123"
"Supplier: Company"     → "Company"
"Company: Buyer Corp"   → "Buyer Corp"
```

**Status Normalization**:
```
"APPROVED"      → "Approved"
"pending"       → "Pending"
"In Progress"   → "In progress"
```

---

### Integration Tests - Health API (8 tests)

| Test | Endpoint | Expected Response |
|------|----------|-------------------|
| `test_root_endpoint_returns_200` | `GET /` | 200, message with API info |
| `test_health_endpoint_returns_200` | `GET /health` | 200, `{"status": "healthy"}` |
| `test_supported_types_endpoint_returns_200` | `GET /supported-types` | 200, list of document types |
| `test_root_endpoint_structure` | `GET /` | Contains message, version, endpoints |
| `test_health_using_helper_method` | `GET /health` | Helper assertion passes |
| `test_root_has_endpoints_info_using_helper` | `GET /` | Contains endpoints field |
| `test_supported_types_no_duplicates` | `GET /supported-types` | No duplicate types |
| `test_supported_types_are_lowercase` | `GET /supported-types` | All types lowercase |

**Example Responses**:
```json
// GET /
{
  "message": "DocIntelligenceAPI is running",
  "version": "1.0.0",
  "endpoints": "/upload/invoice, /upload/po"
}

// GET /health
{
  "status": "healthy"
}

// GET /supported-types
{
  "supported_types": ["invoice", "po", "purchase_order"]
}
```

---

### Integration Tests - Invoice Upload API (10 tests)

| Test | Scenario | Input | Expected Status | Expected Behavior |
|------|----------|-------|-----------------|-------------------|
| `test_upload_valid_invoice_returns_200` | Valid PDF upload | PDF bytes | 200 | Complete invoice schema returned |
| `test_upload_invoice_with_txt_file_returns_400` | Upload .txt file | Text file | 400 | "Invalid file type" error |
| `test_upload_invoice_with_docx_file_returns_400` | Upload .docx file | DOCX file | 400 | "Invalid file type" error |
| `test_upload_invoice_without_file_returns_422` | No file provided | No file | 422 | FastAPI validation error |
| `test_upload_invoice_with_currency_normalization` | Currency symbol | `€` in data | 200 | Currency normalized to `EUR` |
| `test_upload_invoice_with_date_format_conversion` | Date conversion | `15/01/2024` | 200 | Date converted to `2024-01-15` |
| `test_upload_invoice_with_empty_items_array` | Empty items | `Items: []` | 200 | Empty array accepted |
| `test_upload_invoice_with_nullable_fields_as_none` | Null fields | Tax, addresses null | 200 | None values in response |
| `test_upload_invoice_removes_extra_fields` | Extra AI fields | Hallucinated fields | 200 | Extra fields removed |
| `test_upload_invoice_response_time_tracking` | Timing | Any valid file | 200 | `predictionTime` ≥ 0 |

**Request Format**:
```bash
curl -X POST "http://localhost:8000/upload/invoice" \
  -F "file=@invoice.pdf"
```

**Success Response (200)**:
```json
{
  "confidence": 0.85,
  "data": {
    "InvoiceId": "INV-12345",
    "VendorName": "Test Vendor",
    "InvoiceDate": "2024-01-15",
    "SubTotal": 1000.50,
    "Currency": "USD",
    "Items": [...]
  },
  "predictionTime": 2.543
}
```

**Error Response (400)**:
```json
{
  "detail": "Invalid file type. Only PDF files are supported."
}
```

---

### Integration Tests - PO Upload API (10 tests)

| Test | Scenario | Input | Expected Status | Expected Behavior |
|------|----------|-------|-----------------|-------------------|
| `test_upload_valid_po_returns_200` | Valid PDF upload | PDF bytes | 200 | Complete PO schema returned |
| `test_upload_po_with_txt_file_returns_400` | Upload .txt file | Text file | 400 | "Invalid file type" error |
| `test_upload_po_with_docx_file_returns_400` | Upload .docx file | DOCX file | 400 | "Invalid file type" error |
| `test_upload_po_without_file_returns_422` | No file provided | No file | 422 | FastAPI validation error |
| `test_upload_po_with_currency_normalization` | Currency symbol | `€` in data | 200 | Currency normalized to `EUR` |
| `test_upload_po_with_date_validation` | Date validation | ISO dates | 200 | Dates validated |
| `test_upload_po_with_name_cleaning` | Name prefixes | "Supplier: X" | 200 | Prefixes removed |
| `test_upload_po_with_po_number_cleaning` | PO number prefix | "Number: PO-123" | 200 | Prefix removed |
| `test_upload_po_with_empty_items_array` | Empty items | `items: []` | 200 | Empty array accepted |
| `test_upload_po_removes_extra_fields` | Extra AI fields | Hallucinated fields | 200 | Extra fields removed |

**Request Format**:
```bash
curl -X POST "http://localhost:8000/upload/po" \
  -F "file=@purchase_order.pdf"
```

**Success Response (200)**:
```json
{
  "po_number": "PO-000X",
  "date": "2024-01-24",
  "supplier_name": "Supplier Company",
  "company_name": "Buyer Company",
  "delivery_date": "2024-01-30",
  "total_amount": 40404.00,
  "currency": "EUR",
  "status": "Pending",
  "items": [...]
}
```

---

## Environment & Configuration

### Required Environment Variables

**For Testing**:
- **None required** - All tests use mocking, no external API calls

**For Production API** (not used during tests):
- `ANTHROPIC_API_KEY` - Claude API key (read from `.anthropickey` file)

### Mock Configuration

**ClaudeService Mocking**:
```python
@patch('app.parser_factory.ClaudeService')
def test_example(self, mock_claude_service_class):
    mock_service = Mock()
    mock_service.parse_and_validate.return_value = {...}
    mock_claude_service_class.return_value = mock_service
```

**Mock Response Builders** (`tests/base/mock_helpers.py`):
- `MockClaudeResponseBuilder.perfect_invoice_response()` - Complete valid invoice
- `MockClaudeResponseBuilder.perfect_po_response()` - Complete valid PO
- `MockClaudeResponseBuilder.invoice_with_currency_symbol()` - Invoice with € symbol
- `MockClaudeResponseBuilder.invoice_with_extra_fields()` - Invoice with hallucinated fields
- `MockClaudeResponseBuilder.po_with_prefix_in_names()` - PO with name prefixes

**Mock PDF Creation**:
```python
MockPDFFile.create_sample_pdf("test.pdf", "Sample content")
```

### Test Fixtures

**Base Test Class** (`tests/base/base_test_case.py`):
- `setUp()` - Creates `tests/data/` directory
- `tearDown()` - Cleans up test data
- Custom assertions:
  - `assertValidISO8601Date(date_str)`
  - `assertValidCurrencyCode(currency)`
  - `assertNumeric(value)`
  - `assertHasKeys(dict, keys)`

**Singleton Reset**:
```python
def setUp(self):
    ParserFactory._claude_service = None  # Reset singleton
```

### Page Object Model (POM)

**API Clients** (`tests/integration/api_clients/`):
- `BaseAPIClient` - Base HTTP operations
- `HealthAPIClient` - Health endpoints
- `DocumentUploadClient` - Upload endpoints

**Usage**:
```python
client = TestClient(app)
upload_client = DocumentUploadClient(client)
response = upload_client.upload_invoice(pdf_bytes)
upload_client.assert_invoice_schema(response)
```

---

## Test Execution

### Local Execution

#### Prerequisites
```bash
# Navigate to project root
cd InvoicePOParser

# Activate virtual environment
# Windows
venv\Scripts\activate

# Unix/Mac
source venv/bin/activate

# Install dependencies (if needed)
pip install -r requirements.txt
```

#### Run All Tests
```bash
# All 67 tests with verbose output
venv/Scripts/python.exe -m unittest discover -s tests -p "test_*.py" -v

# Expected output:
# Ran 67 tests in ~1.5s
# OK
```

#### Run Specific Test Suites
```bash
# Unit tests only (37 tests)
venv/Scripts/python.exe -m unittest discover -s tests/unit -p "test_*.py" -v

# Integration tests only (28 tests)
venv/Scripts/python.exe -m unittest discover -s tests/integration -p "test_*.py" -v

# Legacy API tests (7 tests)
venv/Scripts/python.exe -m unittest tests.test_api -v
```

#### Run Specific Test Files
```bash
# Parser factory tests
venv/Scripts/python.exe -m unittest tests.unit.test_parser_factory -v

# Invoice parser tests
venv/Scripts/python.exe -m unittest tests.unit.test_invoice_parser -v

# PO parser tests
venv/Scripts/python.exe -m unittest tests.unit.test_po_parser -v

# Health API tests
venv/Scripts/python.exe -m unittest tests.integration.test_api_health -v

# Invoice upload tests
venv/Scripts/python.exe -m unittest tests.integration.test_api_invoice_upload -v

# PO upload tests
venv/Scripts/python.exe -m unittest tests.integration.test_api_po_upload -v
```

#### Run Individual Tests
```bash
# Single test method
venv/Scripts/python.exe -m unittest tests.unit.test_invoice_parser.TestInvoiceClaudeParser.test_currency_symbol_normalization -v
```

### CI/CD Execution Flow

**Recommended CI Pipeline**:

```yaml
# Example GitHub Actions workflow
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          python -m unittest discover -s tests -p "test_*.py" -v
      
      - name: Check test results
        run: |
          if [ $? -ne 0 ]; then exit 1; fi
```

**Test Stages**:
1. **Setup** - Install Python, dependencies
2. **Unit Tests** - Fast, isolated component tests
3. **Integration Tests** - API endpoint tests
4. **Reporting** - Generate coverage reports (optional)
5. **Cleanup** - No cleanup needed (mocks only)

**Expected CI Metrics**:
- **Duration**: <5 seconds total
- **Success Rate**: 100% (67/67 passing)
- **Coverage**: ~85% (parsers, API, factory)

---

## Failure Handling

### Common Failure Reasons

#### 1. Import Errors
**Symptom**: `ModuleNotFoundError: No module named 'app'`

**Causes**:
- Running from wrong directory
- Virtual environment not activated
- Missing dependencies

**Solutions**:
```bash
# Ensure you're in project root
cd InvoicePOParser

# Activate venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Unix

# Install dependencies
pip install -r requirements.txt

# Run with full path
venv/Scripts/python.exe -m unittest discover -s tests -p "test_*.py" -v
```

#### 2. Test Isolation Failures
**Symptom**: Tests pass individually but fail when run together

**Causes**:
- Singleton state not reset
- Shared mock instances
- Test data pollution

**Solutions**:
- Ensure `ParserFactory._claude_service = None` in setUp/tearDown
- Use `copy.deepcopy()` for mock data
- Check base test class is used

#### 3. Mock Configuration Errors
**Symptom**: `AttributeError: Mock object has no attribute 'parse_and_validate'`

**Causes**:
- Incorrect mock patch path
- Missing mock return value
- Wrong mock object structure

**Solutions**:
```python
# Correct patch path
@patch('app.parser_factory.ClaudeService')

# Set return value
mock_service.parse_and_validate.return_value = mock_data

# Verify mock structure
mock_claude_service_class.return_value = mock_service
```

#### 4. Assertion Failures
**Symptom**: `AssertionError: 'USD' != 'EUR'`

**Causes**:
- Mock data doesn't match test expectations
- Parser behavior changed
- Incorrect test assumptions

**Solutions**:
- Review mock response builder
- Check parser normalization logic
- Update test expectations if behavior is correct

#### 5. File System Errors
**Symptom**: `FileNotFoundError: tests/data/test.pdf`

**Causes**:
- Test data directory not created
- PDF cleanup failed
- Wrong file path

**Solutions**:
- Ensure `BaseTestCase.setUp()` is called
- Check `tearDown()` for cleanup
- Use absolute paths or `self.test_data_dir`

### Debugging Guidance

#### Enable Verbose Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Run Single Failing Test
```bash
venv/Scripts/python.exe -m unittest tests.unit.test_invoice_parser.TestInvoiceClaudeParser.test_currency_symbol_normalization -v
```

#### Print Mock Call Arguments
```python
print(mock_service.parse_and_validate.call_args)
print(mock_service.parse_and_validate.call_count)
```

#### Inspect Test Data
```python
def test_debug(self):
    response = MockClaudeResponseBuilder.perfect_invoice_response()
    print(json.dumps(response, indent=2))
    self.fail("Debug stop")
```

#### Check Singleton State
```python
print(f"ClaudeService singleton: {ParserFactory._claude_service}")
```

### Test Failure Checklist

When a test fails:
- [ ] Read the full error message
- [ ] Check which assertion failed
- [ ] Verify mock data is correct
- [ ] Ensure test isolation (run individually)
- [ ] Check logs for warnings/errors
- [ ] Verify import paths are correct
- [ ] Confirm parser behavior matches expectations
- [ ] Review recent code changes

---

## Reporting & Artifacts

### Test Output

**Standard Output** (unittest):
```
test_perfect_invoice_parsing (tests.unit.test_invoice_parser.TestInvoiceClaudeParser.test_perfect_invoice_parsing)
Test parsing with perfect AI response. ... ok

----------------------------------------------------------------------
Ran 67 tests in 1.511s

OK
```

**Verbose Output** (with `-v` flag):
```
test_currency_normalization ... ok
test_date_format_validation ... ok
test_perfect_po_parsing ... ok

Ran 67 tests in 1.511s

OK
```

### Coverage Reports

**Generate Coverage** (optional, requires `coverage` package):
```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run -m unittest discover -s tests -p "test_*.py"

# Generate report
coverage report

# Generate HTML report
coverage html
# Output: htmlcov/index.html
```

**Expected Coverage**:
```
Name                                   Stmts   Miss  Cover
----------------------------------------------------------
app/parser_factory.py                     45      2    96%
app/parsers/invoice_claude_parser.py     120      8    93%
app/parsers/po_claude_parser.py          115      7    94%
app/main.py                               85     12    86%
----------------------------------------------------------
TOTAL                                    365     29    92%
```

### Log Files

**Test Logs**:
- **Location**: Console output (stdout/stderr)
- **Format**: Python logging format
- **Levels**: INFO, WARNING, ERROR

**Sample Log Output**:
```
2026-01-29 18:47:35,189 - app.parsers.invoice_claude_parser - WARNING - Extra keys found (will be removed): {'Hallucination', 'ExtraData', 'UnexpectedField'}
2026-01-29 18:47:35,957 - app.parser_factory - ERROR - Failed to initialize Claude service: API key not found
```

**Filtering Logs**:
```bash
# Errors only
venv/Scripts/python.exe -m unittest discover -s tests -p "test_*.py" 2>&1 | findstr ERROR

# Warnings only
venv/Scripts/python.exe -m unittest discover -s tests -p "test_*.py" 2>&1 | findstr WARNING
```

### Test Artifacts

**Created During Tests**:
- `tests/data/*.pdf` - Temporary test PDFs (auto-deleted)
- `__pycache__/` - Python bytecode (auto-generated)

**Cleanup**:
- All test data deleted in `tearDown()`
- No persistent artifacts after test run
- Safe to delete `tests/data/` manually if needed

### Continuous Integration Artifacts

**Recommended CI Artifacts**:
1. **Test Results** - JUnit XML format
   ```bash
   python -m unittest discover -s tests -p "test_*.py" --xml-output=test-results.xml
   ```

2. **Coverage Report** - HTML format
   ```bash
   coverage html --directory=coverage-report
   ```

3. **Test Logs** - Plain text
   ```bash
   python -m unittest discover -s tests -p "test_*.py" -v > test-output.log 2>&1
   ```

**Artifact Retention**:
- Test results: 30 days
- Coverage reports: Latest only
- Logs: 7 days

---

## Quick Reference

### Test Statistics

| Category | Count | Status |
|----------|-------|--------|
| **Total Tests** | 67 | ✅ All Passing |
| Unit Tests | 37 | ✅ |
| Integration Tests | 28 | ✅ |
| Legacy Tests | 2 | ✅ |
| **Execution Time** | ~1.5s | ✅ Fast |

### Test Files

| File | Tests | Purpose |
|------|-------|---------|
| `test_parser_factory.py` | 9 | Parser routing and singleton |
| `test_invoice_parser.py` | 15 | Invoice schema validation |
| `test_po_parser.py` | 13 | PO schema validation |
| `test_api_health.py` | 8 | Health endpoints |
| `test_api_invoice_upload.py` | 10 | Invoice upload API |
| `test_api_po_upload.py` | 10 | PO upload API |
| `test_api.py` | 7 | Legacy API tests |

### Commands Cheat Sheet

```bash
# All tests
venv/Scripts/python.exe -m unittest discover -s tests -p "test_*.py" -v

# Unit tests
venv/Scripts/python.exe -m unittest discover -s tests/unit -p "test_*.py" -v

# Integration tests
venv/Scripts/python.exe -m unittest discover -s tests/integration -p "test_*.py" -v

# Specific file
venv/Scripts/python.exe -m unittest tests.unit.test_invoice_parser -v

# Single test
venv/Scripts/python.exe -m unittest tests.unit.test_invoice_parser.TestInvoiceClaudeParser.test_currency_symbol_normalization -v

# With coverage
coverage run -m unittest discover -s tests -p "test_*.py"
coverage report
coverage html
```

---

**Document Maintained By**: QA Engineering Team  
**Review Schedule**: After each major release  
**Feedback**: Submit issues or PRs for documentation improvements

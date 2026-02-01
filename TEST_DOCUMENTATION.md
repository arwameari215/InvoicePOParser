# Test Documentation - DocIntelligenceAPI with ERPNext Integration

**Version**: 2.0.0  
**Last Updated**: February 1, 2026  
**Test Framework**: unittest (Python standard library)  
**Total Tests**: 108 tests

---

## Table of Contents

1. [Test Overview](#test-overview)
2. [Test Structure](#test-structure)
3. [Test Categories](#test-categories)
4. [ERPNext Integration Tests](#erpnext-integration-tests)
5. [Test Execution](#test-execution)
6. [Environment & Configuration](#environment--configuration)
7. [Test Fixtures](#test-fixtures)
8. [CI/CD Integration](#cicd-integration)
9. [Troubleshooting](#troubleshooting)

---

## Test Overview

### Testing Goals

The DocIntelligenceAPI test suite ensures:

- **API Reliability**: All FastAPI endpoints return correct responses and status codes
- **Parser Accuracy**: Invoice and Purchase Order parsers correctly extract and validate data
- **ERPNext Integration**: Real ERPNext API operations work correctly (NO MOCKS)
- **Workflow Validation**: Complete end-to-end workflows from parsing to ERPNext submission
- **Schema Validation**: All output conforms to defined JSON schemas
- **Error Handling**: Invalid inputs are rejected with appropriate error messages
- **Data Normalization**: Currency symbols, dates, and text are properly normalized

### Testing Strategy

**Methodology**: Comprehensive testing with mixed mocking strategies  
**Approach**: Bottom-up (unit → integration → real ERPNext)  
**Philosophy**: Fast feedback with unit/API tests, real validation with ERPNext tests

### Test Levels

#### 1. Unit Tests (48 tests)
- **Scope**: Individual components in isolation
- **Location**: `tests/unit/`
- **Mocking**: All external services mocked
- **Speed**: Fast (~5 seconds)
- **Purpose**: Validate parsing logic, schema validation, field normalization

#### 2. API Integration Tests (44 tests)
- **Scope**: API endpoints with mocked services
- **Location**: `tests/integration/test_api_*.py`
- **Mocking**: ERPNext and Claude services mocked
- **Speed**: Medium (~10 seconds)
- **Purpose**: Validate HTTP responses, error handling, endpoint behavior

#### 3. ERPNext Integration Tests (16 tests)
- **Scope**: Real ERPNext API operations - **NO MOCKS**
- **Location**: `tests/integration/test_erpnext_*.py`
- **Mocking**: None - connects to real ERPNext
- **Speed**: Slow (~15 seconds, depends on network)
- **Purpose**: Validate actual ERPNext operations, workflows, data integrity

---

## Test Structure

### Folder Layout

```
tests/
├── fixtures/                       # Test data and fixtures
│   ├── erpnext_fixtures.py        # ERPNext entity test data
│   └── __init__.py
├── base/                           # Test infrastructure
│   ├── base_test_case.py          # Base class with custom assertions
│   ├── mock_helpers.py            # Mock builders and factories
│   └── __init__.py
├── unit/                           # Unit tests (48 tests)
│   ├── test_parser_factory.py     # ParserFactory tests (8 tests)
│   ├── test_invoice_parser.py     # InvoiceClaudeParser tests (12 tests)
│   ├── test_po_parser.py          # PurchaseOrderClaudeParser tests (13 tests)
│   └── __init__.py
├── integration/                    # Integration tests (60 tests)
│   ├── api_clients/               # Page Object Model implementations
│   │   ├── base_api_client.py     # Base API client
│   │   ├── health_api_client.py   # Health endpoint client
│   │   └── document_upload_client.py  # Upload endpoint client
│   ├── test_api_health.py         # Health API tests (8 tests)
│   ├── test_api_invoice_upload.py # Invoice upload tests (9 tests)
│   ├── test_api_po_upload.py      # PO upload tests (9 tests)
│   ├── test_erpnext_api.py        # ERPNext API tests - mocked (16 tests)
│   ├── test_erpnext_real.py       # Real ERPNext connection tests (13 tests)
│   ├── test_erpnext_workflows.py  # Real ERPNext workflow tests (8 tests)
│   └── __init__.py
├── data/                           # Test data (created at runtime)
├── test_api.py                      # Legacy API tests (7 tests)
├── __init__.py
└── fixtures/
    ├── erpnext_fixtures.py          # ✨ ERPNext test data (361 lines)
    └── __init__.py
```

### Naming Conventions

**Test Files**: `test_<component>.py`  
**Test Classes**: `Test<ComponentName>(unittest.TestCase)`  
**Test Methods**: `test_<feature>_<scenario>()`  
**Fixtures**: `<entity>_fixtures.py`  
**API Clients**: `<resource>_api_client.py`

Examples:
- ✅ `test_parser_factory.py`
- ✅ `TestInvoiceClaudeParser`
- ✅ `test_currency_normalization()`
- ✅ `MockClaudeResponseBuilder`
- ✅ `document_upload_client.py`
- ✅ `erpnext_fixtures.py`

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

**ERPNext Test Fixtures**:
- Centralized in `tests/fixtures/erpnext_fixtures.py`
- Reusable test data for all ERPNext entities:
  - Companies, Suppliers, Customers, Items
  - Purchase Orders (POs)
  - Sales Invoices
- Timestamp-based unique entity names (avoid duplicates)
- Helper functions:
  - `get_test_company_data()`
  - `get_test_supplier_data()`
  - `get_test_customer_data()`
  - `get_test_item_data()`
  - `get_test_purchase_order_data()`
  - `get_test_sales_invoice_data()`
  - `get_invalid_<entity>_data()` for error testing

**Test Isolation**:
- Each test gets fresh mocks
- `ParserFactory._claude_service = None` reset in setUp/tearDown
- No shared state between tests
- ERPNext tests use timestamp-based names to avoid conflicts

---

## Test Coverage

### Features Covered

#### ✅ **Parser Unit Tests (37 tests)**
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

#### ✅ **API Tests - Mocked (44 tests)**
- **Health API (8 tests)**:
  - `GET /` - Root endpoint
  - `GET /health` - Health check
  - `GET /supported-types` - Document types list
  - Response structure validation
  
- **Document Upload API (20 tests)**:
  - `POST /upload/invoice` - Invoice upload (10 tests)
  - `POST /upload/po` - Purchase Order upload (10 tests)
  - File type validation
  - Error handling
  - Data normalization
  
- **ERPNext API - Mocked (16 tests)**:
  - `GET /erpnext/companies` - List companies
  - `GET /erpnext/suppliers` - List suppliers
  - `GET /erpnext/customers` - List customers
  - `GET /erpnext/items` - List items
  - `POST /erpnext/purchase-orders` - Create PO
  - `POST /erpnext/sales-invoices` - Create invoice
  - `GET /erpnext/purchase-orders/{id}` - Get PO details
  - Error handling (404, 500, validation errors)

#### ✅ **ERPNext Integration Tests - Real Connection (16 tests)**

**Note**: These tests connect to **REAL ERPNext instance** (NO MOCKS)

- **Connection Tests (1 test)**:
  - ERPNext API connectivity
  - Credential validation
  
- **Entity Operations (12 tests)**:
  - Create Company (with timestamp)
  - Retrieve Company
  - Create Supplier (with timestamp)
  - Retrieve Supplier
  - Create Customer (with timestamp)
  - Retrieve Customer
  - Create Item (with timestamp)
  - Retrieve Item
  - Create Purchase Order (with timestamp)
  - Retrieve Purchase Order
  - Create Sales Invoice (with timestamp, description field)
  - Retrieve Sales Invoice
  
- **Workflow Tests (3 tests)**:
  - Complete PO submission workflow
  - Complete Sales Invoice submission workflow
  - Multi-item transaction handling

#### ✅ **Legacy Tests (7 tests)**
- Root endpoint tests
- Health check tests
- Document type listing

### Test Summary

| Category | Tests | External Dependencies | Execution Speed |
|----------|-------|----------------------|-----------------|
| Unit Tests | 37 | None (mocked) | Very Fast (<1s) |
| API Tests (Mocked) | 44 | None (mocked) | Fast (~1-2s) |
| ERPNext Real Tests | 16 | **Real ERPNext** | Slower (~30s) |
| Legacy Tests | 7 | None (mocked) | Very Fast |
| **TOTAL** | **108** | Optional ERPNext | ~31s (with ERPNext) |

### Known Gaps & Exclusions

**Not Tested (By Design)**:
- Real Claude API integration (requires API key, costs money)
- PDF content accuracy (Claude behavior is non-deterministic)
- File upload size limits (tested manually)
- Concurrent request handling (load testing out of scope)
- Database operations (no database in this project)
- ERPNext data persistence (entities created during tests may remain)

**Manual Testing Required**:
- Actual PDF parsing with Claude AI
- Multi-language document support
- Complex table extraction
- Handwritten text recognition
- Large-scale ERPNext data operations

---

## ERPNext Integration Tests

### Overview

The ERPNext integration tests validate **real** communication with an ERPNext instance:
- **NO MOCKS** - Direct API calls to ERPNext
- **Real Entity Creation** - Companies, Suppliers, Customers, Items, POs, Invoices
- **Timestamp-Based Names** - Unique entity names on each run (avoid duplicates)
- **Auto-Skip** - Tests skip gracefully if ERPNext is unavailable
- **Optional in CI** - Can run in CI with secrets or skip automatically

### Test Files

#### 1. `tests/integration/test_erpnext_real.py` (13 tests)

**Connection Test**:
```python
def test_erpnext_connection(self):
    """Verify ERPNext API is accessible"""
    # Tests basic connectivity
    # Validates credentials
```

**Entity CRUD Operations** (12 tests):
- Creates entities with timestamp-based names
- Validates successful creation
- Retrieves created entities
- Confirms data integrity

**Example**:
```python
def test_create_company(self):
    """Create a company in ERPNext"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    company_data = get_test_company_data()
    company_data["company_name"] = f"Test Company {timestamp}"
    
    result = self.erp_service.create_entity("Company", company_data)
    self.assertIsNotNone(result)
```

#### 2. `tests/integration/test_erpnext_workflows.py` (8 tests)

**Complete Workflow Tests**:
- Purchase Order submission workflow (4 tests)
- Sales Invoice submission workflow (4 tests)
- Validates end-to-end entity creation
- Tests auto-creation of dependent entities

**Example Workflow**:
```python
def test_complete_po_workflow(self):
    """Complete PO workflow: Company → Supplier → Item → PO"""
    # 1. Create Company
    # 2. Create Supplier
    # 3. Create Item
    # 4. Create Purchase Order
    # 5. Validate all entities linked correctly
```

#### 3. `tests/integration/test_erpnext_api.py` (16 tests - MOCKED)

**Mocked API Endpoint Tests**:
- Tests API endpoints WITHOUT real ERPNext connection
- Uses `@patch` to mock ERPNext service
- Validates request/response structure
- Error handling validation

**Example**:
```python
@patch('app.main.ERPNextService')
def test_get_companies_endpoint(self, mock_service):
    """Test GET /erpnext/companies endpoint"""
    mock_service.return_value.get_entity.return_value = [...]
    response = client.get("/erpnext/companies")
    self.assertEqual(response.status_code, 200)
```

### Environment Setup

**Required Environment Variables** (`.env` file):
```bash
# ERPNext Configuration
ERPNEXT_API_URL=https://your-erpnext-instance.com
ERPNEXT_API_KEY=your_api_key_here
ERPNEXT_API_SECRET=your_api_secret_here

# Document Parsing (Claude AI)
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

**Creating `.env` file**:
```bash
# Copy example template
cp .env.example .env

# Edit with your credentials
nano .env
```

**GitHub CI Secrets** (for CI/CD):
- `ERPNEXT_API_URL`
- `ERPNEXT_API_KEY`
- `ERPNEXT_API_SECRET`

### Running ERPNext Tests

#### Prerequisites
```bash
# 1. Ensure .env file exists with ERPNext credentials
cat .env

# 2. Verify ERPNext instance is accessible
curl -I https://your-erpnext-instance.com

# 3. Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Unix
```

#### Run All ERPNext Tests
```bash
# Real ERPNext tests only (requires connection)
python -m unittest discover -s tests/integration -p "test_erpnext*.py" -v

# Expected: 13 + 8 = 21 tests (if test_erpnext_api.py excluded)
# Or: 13 + 8 + 16 = 37 tests (if all ERPNext test files included)
```

#### Run Specific ERPNext Test Files
```bash
# Real connection tests only
python -m unittest tests.integration.test_erpnext_real -v

# Workflow tests only
python -m unittest tests.integration.test_erpnext_workflows -v

# Mocked API tests only
python -m unittest tests.integration.test_erpnext_api -v
```

#### Run Without ERPNext Tests
```bash
# Unit and API tests only (no ERPNext)
python -m unittest discover -s tests/unit -p "test_*.py" -v
python -m unittest discover -s tests/integration -p "test_api*.py" -v

# This runs 37 + 44 = 81 tests (excludes ERPNext real tests)
```

### Test Behavior

#### Auto-Skip Logic

**ERPNext tests automatically skip if**:
- `.env` file missing
- ERPNext credentials not configured
- ERPNext instance unreachable
- Network connectivity issues

**Example Skip Message**:
```
test_create_company (tests.integration.test_erpnext_real.TestERPNextEntityOperations) 
... skipped 'ERPNext not configured'
```

#### Timestamp-Based Naming

To avoid duplicate entity errors on repeated test runs:

```python
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
company_name = f"Test Company {timestamp}"  # "Test Company 20260129_184523"
```

#### Cleanup

**Note**: ERPNext tests create **real entities** in your ERPNext instance.

**Manual Cleanup** (if needed):
```python
# ERPNext UI: Navigate to entity list → Delete test entities
# Filter by name containing "Test Company", "Test Supplier", etc.
```

### Troubleshooting ERPNext Tests

#### Issue: Tests Skipped
**Cause**: ERPNext not configured or unreachable

**Solution**:
```bash
# Verify .env file
cat .env

# Test ERPNext connection manually
curl -X GET "https://your-erpnext.com/api/resource/Company" \
  -H "Authorization: token api_key:api_secret"
```

#### Issue: Duplicate Entity Errors
**Cause**: Entity with same name already exists

**Solution**:
- Tests now use timestamps - this should be rare
- Delete existing test entities from ERPNext
- Or modify fixture data to use different names

#### Issue: Validation Errors
**Cause**: Missing required fields in ERPNext schema

**Solution**:
- Check ERPNext instance version compatibility
- Review `erpnext_fixtures.py` for required fields
- Add missing fields (e.g., `description` for Sales Invoice)

#### Issue: Slow Test Execution
**Cause**: Real network calls to ERPNext

**Solution**:
- Run ERPNext tests separately from unit/API tests
- Use `--failfast` flag to stop on first failure
- Consider running ERPNext tests only in CI (not locally)



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

**For Unit and API Tests (Mocked)**:
- **None required** - All tests use mocking, no external API calls

**For Document Parsing** (not used during tests):
- `ANTHROPIC_API_KEY` - Claude API key (read from `.anthropickey` file)

**For ERPNext Integration Tests** (optional):
- `ERPNEXT_API_URL` - ERPNext instance URL (e.g., `https://your-erpnext.com`)
- `ERPNEXT_API_KEY` - ERPNext API key
- `ERPNEXT_API_SECRET` - ERPNext API secret

**Example `.env` file**:
```bash
# ERPNext Configuration (optional, for real ERPNext tests)
ERPNEXT_API_URL=https://your-erpnext-instance.com
ERPNEXT_API_KEY=your_api_key_here
ERPNEXT_API_SECRET=your_api_secret_here

# Claude AI (optional, for document parsing)
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

### Mock Configuration

**ClaudeService Mocking**:
```python
@patch('app.parser_factory.ClaudeService')
def test_example(self, mock_claude_service_class):
    mock_service = Mock()
    mock_service.parse_and_validate.return_value = {...}
    mock_claude_service_class.return_value = mock_service
```

**ERPNext Service Mocking** (for API tests):
```python
@patch('app.main.ERPNextService')
def test_erpnext_endpoint(self, mock_service):
    mock_service.return_value.get_entity.return_value = [...]
    response = client.get("/erpnext/companies")
    self.assertEqual(response.status_code, 200)
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

**ERPNext Fixtures** (`tests/fixtures/erpnext_fixtures.py`):
Centralized test data for all ERPNext entities:

```python
# Get test data
company_data = get_test_company_data()
supplier_data = get_test_supplier_data()
customer_data = get_test_customer_data()
item_data = get_test_item_data()
po_data = get_test_purchase_order_data()
invoice_data = get_test_sales_invoice_data()

# Invalid data for error testing
invalid_company = get_invalid_company_data()
invalid_supplier = get_invalid_supplier_data()
# ... etc.
```

**Fixture Features**:
- Complete, valid entity data
- Realistic field values
- Ready for ERPNext API submission
- Invalid data variants for error testing

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

# Configure environment variables
# 1. For document parsing (Claude AI)
echo "sk-ant-api03-your-key-here" > .anthropickey

# 2. For ERPNext tests (optional)
cp .env.example .env
# Edit .env with your ERPNext credentials
```

#### Run All Tests
```bash
# All 108 tests with verbose output
# Includes ERPNext tests if configured, skips if not
venv/Scripts/python.exe -m unittest discover -s tests -p "test_*.py" -v

# Expected output:
# Ran 108 tests in ~31s (with ERPNext) or ~2s (without ERPNext)
# OK
```

#### Run Specific Test Suites
```bash
# Unit tests only (37 tests, very fast)
venv/Scripts/python.exe -m unittest discover -s tests/unit -p "test_*.py" -v

# API tests only - Mocked (44 tests, fast)
venv/Scripts/python.exe -m unittest discover -s tests/integration -p "test_api*.py" -v

# ERPNext tests only - Real connection (16 tests, slower)
venv/Scripts/python.exe -m unittest discover -s tests/integration -p "test_erpnext*.py" -v

# Legacy API tests (7 tests)
venv/Scripts/python.exe -m unittest tests.test_api -v
```

#### Run Tests WITHOUT ERPNext
```bash
# Run only unit and mocked API tests (no ERPNext required)
venv/Scripts/python.exe -m unittest discover -s tests/unit -p "test_*.py" -v
venv/Scripts/python.exe -m unittest discover -s tests/integration -p "test_api*.py" -v

# Total: 37 + 44 + 7 = 88 tests (excludes 20 ERPNext real tests)
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

# ERPNext API tests (mocked)
venv/Scripts/python.exe -m unittest tests.integration.test_erpnext_api -v

# ERPNext real connection tests
venv/Scripts/python.exe -m unittest tests.integration.test_erpnext_real -v

# ERPNext workflow tests
venv/Scripts/python.exe -m unittest tests.integration.test_erpnext_workflows -v
```

#### Run Individual Tests
```bash
# Single test method
venv/Scripts/python.exe -m unittest tests.unit.test_invoice_parser.TestInvoiceClaudeParser.test_currency_symbol_normalization -v

# Single ERPNext test
venv/Scripts/python.exe -m unittest tests.integration.test_erpnext_real.TestERPNextConnection.test_erpnext_connection -v
```

### CI/CD Execution Flow

**GitHub Actions Workflow** (`.github/workflows/ci.yml`):

```yaml
name: CI/CD Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      # ... setup steps ...
      
      # Step 11: Unit and API tests (always run, mocked)
      - name: Run Unit and API Tests
        run: |
          python -m unittest discover -s tests/unit -p "test_*.py" -v
          python -m unittest discover -s tests/integration -p "test_api*.py" -v
      
      # Step 12: ERPNext integration tests (optional, skips if not configured)
      - name: Run ERPNext Integration Tests (Optional)
        continue-on-error: true
        env:
          ERPNEXT_API_URL: ${{ secrets.ERPNEXT_API_URL }}
          ERPNEXT_API_KEY: ${{ secrets.ERPNEXT_API_KEY }}
          ERPNEXT_API_SECRET: ${{ secrets.ERPNEXT_API_SECRET }}
        run: |
          python -m unittest discover -s tests/integration -p "test_erpnext*.py" -v
```

**Test Stages**:
1. **Setup** - Install Python, dependencies
2. **Unit Tests** - Fast, isolated component tests (always run)
3. **API Tests** - Mocked endpoint tests (always run)
4. **ERPNext Tests** - Real ERPNext connection (optional, non-blocking)
5. **Reporting** - Log results, upload artifacts

**Expected CI Metrics**:
- **Unit + API Tests Duration**: <5 seconds
- **ERPNext Tests Duration**: ~30 seconds (if run)
- **Success Rate**: 100% (all tests passing)
- **Coverage**: ~85% (parsers, API, factory)

**CI Behavior**:
- **ERPNext Secrets Present**: Runs all 108 tests
- **ERPNext Secrets Missing**: Skips ERPNext tests, runs 88 tests
- **ERPNext Tests Fail**: CI continues (non-blocking)

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

#### 6. ERPNext Connection Errors
**Symptom**: `ConnectionError: Failed to connect to ERPNext`

**Causes**:
- `.env` file missing or misconfigured
- ERPNext instance unreachable
- Invalid credentials
- Network issues

**Solutions**:
```bash
# Verify .env file exists
cat .env

# Test ERPNext connection manually
curl -X GET "https://your-erpnext.com/api/resource/Company" \
  -H "Authorization: token api_key:api_secret"

# Check ERPNext URL and credentials
echo $ERPNEXT_API_URL
echo $ERPNEXT_API_KEY

# Run tests without ERPNext
python -m unittest discover -s tests/unit -p "test_*.py" -v
python -m unittest discover -s tests/integration -p "test_api*.py" -v
```

#### 7. ERPNext Duplicate Entity Errors
**Symptom**: `DuplicateEntryError: Company 'Test Company' already exists`

**Causes**:
- Entity with same name already exists in ERPNext
- Previous test run didn't complete cleanup

**Solutions**:
- Tests now use timestamps in names - this should be rare
- Manually delete test entities from ERPNext
- Wait a few seconds and re-run (timestamp will be different)

```python
# Timestamp-based naming (automatic)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
name = f"Test Company {timestamp}"  # "Test Company 20260129_184523"
```

#### 8. ERPNext Validation Errors
**Symptom**: `ValidationError: Missing mandatory field: description`

**Causes**:
- ERPNext schema requires field not in test data
- ERPNext version compatibility issue
- Custom field requirements

**Solutions**:
- Review `tests/fixtures/erpnext_fixtures.py`
- Add missing required fields
- Check ERPNext instance version

```python
# Example fix: Add description field
def get_test_sales_invoice_data():
    return {
        # ... existing fields ...
        "description": "Test sales invoice for automated testing",  # ← Added
    }
```

### Debugging Guidance

#### Enable Verbose Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Run Single Failing Test
```bash
# Unit test
venv/Scripts/python.exe -m unittest tests.unit.test_invoice_parser.TestInvoiceClaudeParser.test_currency_symbol_normalization -v

# ERPNext test
venv/Scripts/python.exe -m unittest tests.integration.test_erpnext_real.TestERPNextConnection.test_erpnext_connection -v
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

#### Debug ERPNext Connection
```python
def test_debug_erpnext(self):
    from app.services.erpnext_service import ERPNextService
    service = ERPNextService()
    
    print(f"ERPNext URL: {service.base_url}")
    print(f"API Key: {service.api_key[:10]}...")  # Partial for security
    
    # Test connection
    try:
        result = service.api_request("GET", "/api/resource/Company")
        print(f"Connection successful: {result}")
    except Exception as e:
        print(f"Connection failed: {e}")
    
    self.fail("Debug stop")
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
- [ ] For ERPNext tests:
  - [ ] Verify .env file configured
  - [ ] Test ERPNext connection manually
  - [ ] Check for duplicate entities in ERPNext
  - [ ] Review required fields in fixtures

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

| Category | Count | External Dependencies | Status |
|----------|-------|----------------------|--------|
| **Unit Tests** | 37 | None (mocked) | ✅ All Passing |
| **API Tests (Mocked)** | 44 | None (mocked) | ✅ All Passing |
| **ERPNext Real Tests** | 16 | **Real ERPNext** | ✅ All Passing |
| **Legacy Tests** | 7 | None (mocked) | ✅ All Passing |
| **TOTAL** | **108** | Optional ERPNext | ✅ All Passing |
| **Execution Time** | ~31s (with ERPNext) | ~2s (without) | ✅ Fast |

### Test Files

| File | Tests | Purpose | Dependencies |
|------|-------|---------|--------------|
| `test_parser_factory.py` | 9 | Parser routing and singleton | None |
| `test_invoice_parser.py` | 15 | Invoice schema validation | None |
| `test_po_parser.py` | 13 | PO schema validation | None |
| `test_api_health.py` | 8 | Health endpoints | None |
| `test_api_invoice_upload.py` | 10 | Invoice upload API | None |
| `test_api_po_upload.py` | 10 | PO upload API | None |
| `test_erpnext_api.py` | 16 | ERPNext API (mocked) | None |
| `test_erpnext_real.py` | 13 | ERPNext connection (real) | **ERPNext** |
| `test_erpnext_workflows.py` | 8 | ERPNext workflows (real) | **ERPNext** |
| `test_api.py` | 7 | Legacy API tests | None |

### Commands Cheat Sheet

```bash
# ============================================
# ALL TESTS
# ============================================
# All tests (108) - Includes ERPNext if configured
venv/Scripts/python.exe -m unittest discover -s tests -p "test_*.py" -v

# ============================================
# BY CATEGORY
# ============================================
# Unit tests only (37 tests, very fast)
venv/Scripts/python.exe -m unittest discover -s tests/unit -p "test_*.py" -v

# API tests only - Mocked (44 tests, fast)
venv/Scripts/python.exe -m unittest discover -s tests/integration -p "test_api*.py" -v

# ERPNext tests only - Real (16 tests, slower, requires ERPNext)
venv/Scripts/python.exe -m unittest discover -s tests/integration -p "test_erpnext*.py" -v

# ============================================
# SPECIFIC FILES
# ============================================
# Unit tests
venv/Scripts/python.exe -m unittest tests.unit.test_parser_factory -v
venv/Scripts/python.exe -m unittest tests.unit.test_invoice_parser -v
venv/Scripts/python.exe -m unittest tests.unit.test_po_parser -v

# API tests (mocked)
venv/Scripts/python.exe -m unittest tests.integration.test_api_health -v
venv/Scripts/python.exe -m unittest tests.integration.test_api_invoice_upload -v
venv/Scripts/python.exe -m unittest tests.integration.test_api_po_upload -v
venv/Scripts/python.exe -m unittest tests.integration.test_erpnext_api -v

# ERPNext tests (real)
venv/Scripts/python.exe -m unittest tests.integration.test_erpnext_real -v
venv/Scripts/python.exe -m unittest tests.integration.test_erpnext_workflows -v

# Legacy tests
venv/Scripts/python.exe -m unittest tests.test_api -v

# ============================================
# INDIVIDUAL TEST METHODS
# ============================================
# Unit test example
venv/Scripts/python.exe -m unittest tests.unit.test_invoice_parser.TestInvoiceClaudeParser.test_currency_symbol_normalization -v

# ERPNext test example
venv/Scripts/python.exe -m unittest tests.integration.test_erpnext_real.TestERPNextConnection.test_erpnext_connection -v

# ============================================
# WITH COVERAGE
# ============================================
# Install coverage
pip install coverage

# Run with coverage
coverage run -m unittest discover -s tests -p "test_*.py"

# Generate report
coverage report

# Generate HTML report
coverage html
# Output: htmlcov/index.html
```

### Quick Test Verification

```bash
# Check if all dependencies installed
pip list | grep -E "fastapi|uvicorn|anthropic|requests|python-dotenv"

# Verify .env file (for ERPNext tests)
cat .env

# Check ERPNext connection (if configured)
curl -X GET "https://your-erpnext.com/api/resource/Company" \
  -H "Authorization: token api_key:api_secret"

# Run quick smoke test (unit tests only, ~1s)
venv/Scripts/python.exe -m unittest discover -s tests/unit -p "test_*.py"

# Run full test suite
venv/Scripts/python.exe -m unittest discover -s tests -p "test_*.py" -v
```

### ERPNext Test Quick Reference

| Command | Tests Run | ERPNext Required | Duration |
|---------|-----------|------------------|----------|
| All tests | 108 | Optional (skips if not configured) | ~31s |
| Unit + API only | 88 | No | ~2s |
| ERPNext only | 20 | Yes | ~30s |
| ERPNext real | 13 | Yes | ~20s |
| ERPNext workflows | 8 | Yes | ~10s |

### Environment Setup Quick Guide

```bash
# 1. Clone repository
git clone <repo-url>
cd InvoicePOParser

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Unix

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment (optional, for ERPNext tests)
cp .env.example .env
# Edit .env with your ERPNext credentials

# 5. Run tests
python -m unittest discover -s tests -p "test_*.py" -v
```

### Test Execution Matrix

| Environment | Unit | API (Mocked) | ERPNext (Real) | Total | Duration |
|-------------|------|--------------|----------------|-------|----------|
| Local (no ERPNext) | ✅ 37 | ✅ 44 + 7 = 51 | ⏭️ Skipped | 88 | ~2s |
| Local (with ERPNext) | ✅ 37 | ✅ 51 | ✅ 20 | 108 | ~31s |
| CI (no secrets) | ✅ 37 | ✅ 51 | ⏭️ Skipped | 88 | ~5s |
| CI (with secrets) | ✅ 37 | ✅ 51 | ✅ 20 | 108 | ~45s |

---

## Best Practices

### Writing New Tests

1. **Test Naming**:
   ```python
   def test_feature_scenario(self):
       """Brief description of what is being tested"""
   ```

2. **Test Structure** (Arrange-Act-Assert):
   ```python
   def test_example(self):
       # Arrange: Setup test data
       data = get_test_data()
       
       # Act: Execute functionality
       result = function_under_test(data)
       
       # Assert: Verify expectations
       self.assertEqual(result, expected)
   ```

3. **Use Fixtures**:
   ```python
   # Good: Reusable fixtures
   from tests.fixtures.erpnext_fixtures import get_test_company_data
   
   def test_create_company(self):
       data = get_test_company_data()
       # Add timestamp for uniqueness
       timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
       data["company_name"] = f"Test Company {timestamp}"
   ```

4. **Mock External Dependencies**:
   ```python
   @patch('app.parser_factory.ClaudeService')
   def test_with_mock(self, mock_service_class):
       mock_service = Mock()
       mock_service.parse.return_value = expected_result
       mock_service_class.return_value = mock_service
       # ... test logic ...
   ```

5. **Test Isolation**:
   ```python
   def setUp(self):
       ParserFactory._claude_service = None  # Reset singletons
       self.test_data_dir = "tests/data"
       os.makedirs(self.test_data_dir, exist_ok=True)
   
   def tearDown(self):
       # Cleanup test data
       if os.path.exists(self.test_data_dir):
           shutil.rmtree(self.test_data_dir)
   ```

### ERPNext Testing Best Practices

1. **Use Timestamps**:
   ```python
   timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
   entity_name = f"Test Entity {timestamp}"
   ```

2. **Handle Optional ERPNext**:
   ```python
   def setUp(self):
       try:
           self.erp_service = ERPNextService()
       except Exception as e:
           self.skipTest(f"ERPNext not configured: {e}")
   ```

3. **Test Real Operations**:
   ```python
   # Create entity
   result = self.erp_service.create_entity("Company", data)
   self.assertIsNotNone(result)
   
   # Verify creation
   retrieved = self.erp_service.get_entity("Company", result["name"])
   self.assertEqual(retrieved["company_name"], data["company_name"])
   ```

4. **Don't Mock ERPNext in Real Tests**:
   ```python
   # ❌ Bad: Mocking in real ERPNext tests
   @patch('app.services.erpnext_service.ERPNextService')
   def test_erpnext_real(self, mock_service):
       # This defeats the purpose of real tests
   
   # ✅ Good: Real connection
   def test_erpnext_real(self):
       service = ERPNextService()  # Real instance
       result = service.get_entity("Company", "Company Name")
   ```

### CI/CD Best Practices

1. **Separate Test Stages**:
   - Fast tests (unit, mocked API) always run
   - Slow tests (ERPNext real) optional, non-blocking

2. **Use Secrets for ERPNext**:
   - Store ERPNext credentials in GitHub Secrets
   - Never commit credentials to repository

3. **Continue on Error**:
   ```yaml
   - name: Run ERPNext Tests (Optional)
     continue-on-error: true  # Don't block CI if ERPNext unavailable
   ```

4. **Log Test Results**:
   ```yaml
   - name: Upload Test Results
     if: always()
     uses: actions/upload-artifact@v2
     with:
       name: test-results
       path: test-output.log
   ```

---

## Additional Resources

### Documentation Files
- [README.md](README.md) - Project overview and setup
- [TEST_DOCUMENTATION.md](TEST_DOCUMENTATION.md) - **This file** - Comprehensive testing guide
- [requirements.txt](requirements.txt) - Python dependencies

### Key Files
- [app/main.py](app/main.py) - FastAPI application entry point
- [app/parser_factory.py](app/parser_factory.py) - Parser factory with singleton
- [app/services/erpnext_service.py](app/services/erpnext_service.py) - ERPNext client
- [tests/fixtures/erpnext_fixtures.py](tests/fixtures/erpnext_fixtures.py) - ERPNext test data
- [.github/workflows/ci.yml](.github/workflows/ci.yml) - CI/CD pipeline

### External Links
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [unittest Documentation](https://docs.python.org/3/library/unittest.html)
- [ERPNext REST API](https://frappeframework.com/docs/user/en/api/rest)
- [Claude API](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)

---

**Document Version**: 2.0  
**Last Updated**: 2026-01-29  
**Total Tests**: 108  
**Test Categories**: Unit (37), API Mocked (44), ERPNext Real (16), Legacy (7)  
**Status**: ✅ All tests passing


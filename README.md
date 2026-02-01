# DocIntelligenceAPI with ERPNext Integration

A production-ready Python backend API for parsing **Invoices** and **Purchase Orders** from PDFs with **integrated ERPNext ERP workflows**. Built with FastAPI and Claude AI, this API extracts structured data from documents and enables seamless automation with ERPNext.

---

## 🚀 Features

### Document Parsing
- ✅ **FastAPI** backend with RESTful endpoints
- ✅ **Claude AI** - Intelligent document parsing using Claude 3.5 Sonnet
- ✅ **OOP architecture** with abstract base classes and factory pattern
- ✅ **PDF parsing** using `pdfplumber` for text extraction
- ✅ **Multi-language support** - English, Hebrew, and more
- ✅ **Currency normalization** - Detects and converts to ISO 4217 codes
- ✅ **Confidence scoring** for extracted fields

### ERPNext Integration
- ✅ **ERPNext REST API** - Direct communication with ERPNext ERP
- ✅ **Entity management** - Companies, Suppliers, Customers, Items
- ✅ **Purchase Order workflow** - Automated PO creation and submission
- ✅ **Sales Invoice workflow** - Automated invoice processing
- ✅ **Entity auto-creation** - Creates missing entities with validation
- ✅ **Token authentication** - Secure API access

### Quality & Testing
- ✅ **108 automated tests** - Comprehensive test coverage
- ✅ **Type hints** and docstrings throughout
- ✅ **Structured logging** for debugging
- ✅ **Production-ready** error handling
- ✅ **CI/CD ready** with GitHub Actions

---

## 📁 Project Structure

```
InvoicePOParser/
├── app/
│   ├── main.py                      # FastAPI app & router mounting
│   ├── parser_factory.py            # Factory for parser selection
│   ├── routers/
│   │   ├── documents.py             # Document upload endpoints
│   │   └── erpnext.py               # ERPNext integration endpoints
│   ├── config/
│   │   ├── prompts.py               # Claude AI prompts
│   │   └── erpnext_config.py        # ERPNext configuration
│   ├── services/
│   │   ├── claude_service.py        # Claude AI client
│   │   └── erpnext_service.py       # ERPNext REST API client
│   ├── workflows/
│   │   └── erpnext_workflows.py     # PO & Invoice workflows
│   ├── parsers/
│   │   ├── base_claude_parser.py    # Abstract base class
│   │   ├── invoice_claude_parser.py # Invoice parser
│   │   └── po_claude_parser.py      # PO parser
│   └── utils/
│       └── pdf_loader.py            # PDF text extraction
├── tests/
│   ├── api/                         # API endpoint tests (51)
│   ├── core/                        # Business logic tests (32)
│   └── integration/                 # ERPNext integration tests (21)
├── .env                             # Environment variables (git-ignored)
├── .anthropickey                    # Claude API key (git-ignored)
├── requirements.txt                 # Python dependencies
├── TEST_DOCUMENTATION.md            # Testing guide
└── README.md                        # This file
```

---

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- pip package manager
- Anthropic API key (required for Claude AI)
- ERPNext instance (optional, for ERP integration)

### Setup Steps

**1. Clone the repository**

```bash
cd InvoicePOParser
```

**2. Create virtual environment**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

### Claude AI Setup (Required)

**1. Get API key** from [Anthropic Console](https://console.anthropic.com/settings/keys)

**2. Create `.anthropickey` file**:

```bash
echo "sk-ant-api03-your-actual-key-here" > .anthropickey
```

⚠️ **Never commit `.anthropickey` to version control!**

### ERPNext Setup (Optional)

**1. Copy environment template**

```bash
cp .env.example .env
```

**2. Edit `.env` with your ERPNext credentials**:

```bash
ERPNEXT_URL=http://localhost:8080
ERPNEXT_API_KEY=your_api_key_here
ERPNEXT_API_SECRET=your_api_secret_here
```

**3. Generate ERPNext API credentials**:
- Log in to ERPNext → User → API Access → Generate Keys
- Copy API Key and Secret to `.env`

⚠️ **Never commit `.env` to version control!**

---

## 🚀 Running the API

Start the server:

```bash
# Standard
python -m uvicorn app.main:app --reload --port 8000

# Using venv explicitly
venv/Scripts/python.exe -m uvicorn app.main:app --reload --port 8000
```

The API will be available at: **http://localhost:8000**

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📡 API Endpoints

### Core Endpoints

**Health Check**

```bash
GET /
GET /health
```

**Response:**
```json
{
  "message": "DocIntelligenceAPI with ERPNext Integration is running",
  "version": "3.0.0",
  "endpoints": {
    "documents": "/upload/invoice, /upload/po, /supported-types",
    "erpnext": "/erpnext/*"
  }
}
```

**Supported Document Types**

```bash
GET /supported-types
```

**Response:**
```json
{
  "supported_types": ["invoice", "po", "purchase_order"]
}
```

### Document Parsing Endpoints

**Upload Invoice**

```bash
POST /upload/invoice
Content-Type: multipart/form-data

# Using curl
curl -X POST "http://localhost:8000/upload/invoice" \
  -F "file=@invoice.pdf"
```

**Response:**
```json
{
  "confidence": 0.85,
  "data": {
    "InvoiceId": "INV-12345",
    "VendorName": "Vendor Company",
    "InvoiceDate": "2024-01-15",
    "BillingAddressRecipient": "Customer Name",
    "ShippingAddress": "123 Main St",
    "SubTotal": 1000.0,
    "ShippingCost": 50.0,
    "InvoiceTotal": 1170.0,
    "Tax": 120.0,
    "Currency": "USD",
    "Items": [
      {
        "description": "Product A",
        "quantity": 2,
        "unit_price": 500.0,
        "total": 1000.0
      }
    ]
  },
  "predictionTime": 2.543
}
```

**Upload Purchase Order**

```bash
POST /upload/po
Content-Type: multipart/form-data

# Using curl
curl -X POST "http://localhost:8000/upload/po" \
  -F "file=@purchase_order.pdf"
```

**Response:**
```json
{
  "po_number": "PO-000X",
  "date": "2024-01-24",
  "supplier_name": "Supplier Company",
  "company_name": "Buyer Company",
  "delivery_date": "2024-01-30",
  "total_amount": 40404.0,
  "currency": "USD",
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

### ERPNext Integration Endpoints

**Test Connection**

```bash
GET /erpnext/test-connection
```

**Get Entity Details**

```bash
GET /erpnext/company/{company_name}
GET /erpnext/supplier/{supplier_name}
GET /erpnext/customer/{customer_name}
GET /erpnext/item/{item_code}
```

**Submit Purchase Order**

```bash
POST /erpnext/purchase-order
Content-Type: application/json

{
  "po_number": "PO-2024-001",
  "supplier": "ABC Supplies",
  "company": "My Company",
  "transaction_date": "2024-01-24",
  "schedule_date": "2024-01-30",
  "currency": "USD",
  "items": [
    {
      "item_code": "ITEM-001",
      "item_name": "Product A",
      "qty": 10,
      "rate": 100.0,
      "amount": 1000.0
    }
  ]
}
```

**Submit Sales Invoice**

```bash
POST /erpnext/sales-invoice
Content-Type: application/json

{
  "customer": "John Doe",
  "company": "My Company",
  "posting_date": "2024-01-24",
  "due_date": "2024-02-24",
  "currency": "USD",
  "items": [
    {
      "item_code": "ITEM-001",
      "qty": 5,
      "rate": 200.0
    }
  ]
}
```

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────┐
│                  Client Application                  │
│            (React/Vue/Angular/Mobile)                │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│          FastAPI Backend (Port 8000)                 │
│                                                      │
│  ┌───────────────┐        ┌──────────────────┐     │
│  │   Documents   │        │     ERPNext      │     │
│  │    Router     │        │     Router       │     │
│  └───────┬───────┘        └────────┬─────────┘     │
│          │                         │                │
│          ▼                         ▼                │
│  ┌───────────────┐        ┌──────────────────┐     │
│  │    Parser     │        │    ERPNext       │     │
│  │   Factory     │        │   Workflows      │     │
│  └───────┬───────┘        └────────┬─────────┘     │
│          │                         │                │
│          ▼                         ▼                │
│  ┌───────────────┐        ┌──────────────────┐     │
│  │  Claude AI    │        │   ERPNext API    │     │
│  │   Service     │        │    Service       │     │
│  └───────────────┘        └────────┬─────────┘     │
└─────────────────────────────────────┼───────────────┘
                                      │
                                      ▼
                          ┌──────────────────────┐
                          │   ERPNext System     │
                          │   (Port 8080)        │
                          └──────────────────────┘
```

### Design Patterns

**1. Factory Pattern** - `ParserFactory`
- Routes to appropriate Claude parser based on document type
- Manages singleton ClaudeService instance
- Supports: "invoice", "po", "purchase_order"

**2. Abstract Base Class** - `BaseClaudeParser`
- Defines interface: `get_prompt()`, `validate_schema()`, `parse()`
- Concrete implementations: `InvoiceClaudeParser`, `PurchaseOrderClaudeParser`

**3. Service Layer**
- `ClaudeService`: Claude AI integration
- `ERPNextService`: ERPNext REST API client
- Separation of concerns between external integrations

**4. Workflow Pattern** - `ERPNextWorkflows`
- End-to-end Purchase Order and Sales Invoice flows
- Entity validation and auto-creation
- Error handling and rollback support

**5. Modular Routers**
- `documents.py`: Document parsing endpoints
- `erpnext.py`: ERPNext integration endpoints
- Clear separation of functionality

---

## 🧪 Testing

### Test Suite (108 Tests)

The project has comprehensive test coverage organized into three categories:

```
tests/
├── api/          # 51 tests - API endpoints (mocked)
├── core/         # 32 tests - Business logic
└── integration/  # 21 tests - ERPNext integration (real)
```

### Running Tests

**All tests:**
```bash
venv/Scripts/python.exe -m unittest discover -s tests -p "test_*.py" -v
```

**By category:**
```bash
# Core tests (32 tests, very fast)
venv/Scripts/python.exe -m unittest discover -s tests/core -p "test_*.py" -v

# API tests (51 tests, fast, mocked)
venv/Scripts/python.exe -m unittest discover -s tests/api -p "test_*.py" -v

# Integration tests (21 tests, requires ERPNext)
venv/Scripts/python.exe -m unittest discover -s tests/integration -p "test_*.py" -v
```

**Fast tests only (no ERPNext):**
```bash
venv/Scripts/python.exe -m unittest discover -s tests/core -p "test_*.py"
venv/Scripts/python.exe -m unittest discover -s tests/api -p "test_*.py"
```

**Specific test file:**
```bash
venv/Scripts/python.exe -m unittest tests.core.parsers.test_invoice_parser -v
```

### Test Categories

**Core Tests (32)** - Business logic
- Parser Factory (9 tests)
- Invoice Parser (15 tests)
- PO Parser (8 tests)
- Zero external dependencies

**API Tests (51)** - Endpoints
- Health API (8 tests)
- Document Upload (20 tests)
- ERPNext API mocked (23 tests)
- All dependencies mocked

**Integration Tests (21)** - ERPNext
- Real CRUD operations (13 tests)
- End-to-end workflows (8 tests)
- Requires ERPNext connection
- Auto-skips if unavailable

For detailed testing documentation, see [TEST_DOCUMENTATION.md](TEST_DOCUMENTATION.md).

---

## 📝 Output Schemas

### Invoice Schema

```json
{
  "confidence": 0.85,
  "data": {
    "InvoiceId": "string",
    "VendorName": "string",
    "InvoiceDate": "YYYY-MM-DD",
    "BillingAddressRecipient": "string | null",
    "ShippingAddress": "string | null",
    "SubTotal": "float",
    "ShippingCost": "float",
    "InvoiceTotal": "float",
    "Tax": "float | null",
    "Currency": "ISO 4217 code (USD, EUR, ILS, etc.)",
    "Items": [
      {
        "description": "string",
        "quantity": "float",
        "unit_price": "float",
        "total": "float"
      }
    ]
  },
  "predictionTime": "float (seconds)"
}
```

### Purchase Order Schema

```json
{
  "po_number": "string",
  "date": "YYYY-MM-DD",
  "supplier_name": "string",
  "company_name": "string",
  "delivery_date": "YYYY-MM-DD",
  "total_amount": "float",
  "currency": "ISO 4217 code",
  "status": "string (Pending, Approved, etc.)",
  "items": [
    {
      "description": "string",
      "quantity": "float",
      "unit_price": "float",
      "total": "float"
    }
  ]
}
```

### Field Notes

**Currency Handling:**
- Detects symbols: $, €, ₪, £, ¥, ₹
- Normalizes to ISO 4217: USD, EUR, ILS, GBP, JPY, INR
- Defaults to USD if not detected

**Date Formats:**
- Input: Various formats (DD/MM/YYYY, MM-DD-YYYY, etc.)
- Output: Always YYYY-MM-DD (ISO 8601)

---

## 🔧 Configuration

### Application Settings

- **Upload Directory**: `tmp/uploads/` (auto-created)
- **Port**: 8000 (configurable)
- **Log Level**: INFO
- **Claude Model**: claude-3-5-sonnet-20241022

### Environment Variables

**.anthropickey file:**
```
sk-ant-api03-your-actual-key-here
```

**.env file (optional):**
```bash
ERPNEXT_URL=http://localhost:8080
ERPNEXT_API_KEY=your_api_key
ERPNEXT_API_SECRET=your_api_secret
```

---

## 🛡️ Error Handling

The API provides meaningful error responses:

**HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid file type, parsing errors)
- `404` - Not Found (file or resource not found)
- `422` - Validation Error (missing required fields)
- `500` - Internal Server Error (unexpected errors)

**Error Response Format:**
```json
{
  "detail": "Error message here"
}
```

All errors are logged with detailed information for debugging.

---

## 📦 Dependencies

### Core
- **fastapi** (>=2.0.0) - Web framework
- **uvicorn[standard]** (>=0.23.0) - ASGI server
- **pydantic** (>=2.0.0) - Data validation
- **python-multipart** (>=0.0.6) - Form data parsing

### Document Processing
- **anthropic** (>=0.18.0) - Claude AI SDK
- **pdfplumber** (>=0.10.0) - PDF text extraction
- **PyPDF2** (>=3.0.0) - PDF processing

### ERPNext Integration
- **requests** (>=2.31.0) - HTTP client
- **python-dotenv** (>=1.0.0) - Environment variables

### Testing
- **pytest** (>=7.4.0) - Testing framework
- **httpx** (>=0.24.0) - HTTP client for tests

---

## 🚀 Deployment

### Production Checklist

- [ ] Set `ANTHROPIC_API_KEY` in production environment
- [ ] Configure ERPNext credentials in `.env`
- [ ] Set up HTTPS/SSL certificates
- [ ] Configure firewall rules
- [ ] Set up monitoring and logging
- [ ] Enable rate limiting
- [ ] Configure CORS if needed
- [ ] Set up backup strategy

### Running in Production

```bash
# Using Gunicorn with Uvicorn workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Or using Docker (create Dockerfile)
docker build -t docintelligenceapi .
docker run -p 8000:8000 docintelligenceapi
```

---

## 🤝 Contributing

### For Document Parsing

1. Create new parser class inheriting from `BaseClaudeParser`
2. Add prompts to `config/prompts.py`
3. Update `ParserFactory` to support new document type
4. Add endpoint in `app/routers/documents.py`
5. Write tests in `tests/core/parsers/`

### For ERPNext Integration

1. Add workflow functions in `app/workflows/erpnext_workflows.py`
2. Extend `ERPNextService` with new methods
3. Add endpoints in `app/routers/erpnext.py`
4. Update configuration in `app/config/erpnext_config.py`
5. Write tests in `tests/integration/`

---

## 📚 Documentation

- **[TEST_DOCUMENTATION.md](TEST_DOCUMENTATION.md)** - Complete testing guide
- **Swagger UI** - http://localhost:8000/docs (interactive API docs)
- **ReDoc** - http://localhost:8000/redoc (alternative API docs)

---

## 🔮 Future Enhancements

- 📦 **Batch Processing** - Multiple document uploads
- 💾 **Caching** - Cache parsed results by PDF hash
- 📊 **Analytics Dashboard** - Parsing metrics and insights
- 🔐 **Authentication** - API key or OAuth2
- 📄 **New Document Types** - Receipts, bills of lading, etc.
- 🎯 **Field-level Confidence** - Confidence per field
- 🔄 **Webhooks** - Real-time ERPNext notifications
- 📈 **Database Integration** - Store parsed data locally

---

## 📞 Support

- Review code documentation and inline docstrings
- Check [TEST_DOCUMENTATION.md](TEST_DOCUMENTATION.md) for testing info
- See [Swagger UI](http://localhost:8000/docs) for API reference

---

## 📜 License

This project is designed for internal use as a document parsing and ERP integration API.

---

**Built with ❤️ using FastAPI, Claude AI, ERPNext, and Python**

**Version 3.0.0** - Enhanced testing, modular architecture, production-ready

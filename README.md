# DocIntelligenceAPI with ERPNext Integration

A standalone Python backend API for parsing **Invoices** and **Purchase Orders (POs)** from PDF files with **integrated ERPNext ERP workflows**. Built with FastAPI and following OOP principles, this API extracts structured data from documents using **Claude AI** and provides seamless integration with ERPNext for automated document submission.

## 🚀 Features

### Document Parsing
- ✅ **FastAPI** backend with RESTful endpoints
- ✅ **Claude AI Integration** - Intelligent document parsing using Claude 3.5 Sonnet
- ✅ **OOP-based architecture** with abstract base classes and concrete implementations
- ✅ **PDF parsing** using `pdfplumber` for text extraction
- ✅ **Factory Pattern** for parser selection with intelligent routing
- ✅ **Multi-language support** - English, Hebrew, and more via Claude AI
- ✅ **Currency extraction** - Detects and normalizes currency codes (USD, EUR, ILS, etc.)
- ✅ **Confidence scoring** for extracted fields (OCI-like output for invoices)

### ERPNext Integration
- ✅ **ERPNext REST API Integration** - Direct communication with ERPNext ERP system
- ✅ **Entity Management** - Fetch and validate Companies, Suppliers, Customers, Items
- ✅ **Purchase Order Workflow** - Complete automation from parsed data to submitted PO
- ✅ **Sales Invoice Workflow** - Automated invoice creation and submission
- ✅ **Token-based Authentication** - Secure ERPNext API access
- ✅ **Entity Auto-creation** - Automatically creates missing entities with validation
- ✅ **Modular Router Architecture** - Separate endpoints for documents and ERPNext

### Quality & Development
- ✅ **Type hints and docstrings** throughout the codebase
- ✅ **Comprehensive logging** for debugging and monitoring
- ✅ **Unit tests** with mocked data
- ✅ **Production-ready** error handling
- ✅ **Modular and extensible** design for future enhancements

## 📁 Project Structure

```
InvoicePOParser/
├── app/
│   ├── main.py                          # FastAPI app initialization & router mounting
│   ├── parser_factory.py                # Factory for Claude parser selection
│   ├── routers/                         # API endpoint routers
│   │   ├── __init__.py
│   │   ├── documents.py                 # Document upload & parsing endpoints
│   │   └── erpnext.py                   # ERPNext integration endpoints
│   ├── config/
│   │   ├── prompts.py                   # Versioned Claude AI prompts
│   │   └── erpnext_config.py            # ERPNext configuration & credentials
│   ├── services/
│   │   ├── claude_service.py            # Claude AI API integration
│   │   └── erpnext_service.py           # ERPNext REST API client
│   ├── workflows/
│   │   └── erpnext_workflows.py         # Purchase Order & Sales Invoice workflows
│   ├── parsers/
│   │   ├── base_claude_parser.py        # Abstract base class
│   │   ├── invoice_claude_parser.py     # Invoice parser implementation
│   │   └── po_claude_parser.py          # Purchase Order parser implementation
│   ├── utils/
│   │   └── pdf_loader.py                # PDF text extraction utilities
│   └── tmp/
│       └── uploads/                     # Temporary file storage
├── tests/
│   ├── unit/                            # Unit tests
│   ├── integration/                     # Integration tests
│   └── test_claude_parsers.py           # Standalone parser testing
├── .env                                 # Environment variables (git-ignored)
├── .env.example                         # Environment template
├── .anthropickey                        # Claude API key (git-ignored)
├── requirements.txt                     # Python dependencies
├── README.md                            # This file
├── ERPNEXT_QUICKSTART.md               # ERPNext integration guide
└── TEST_DOCUMENTATION.md                # Testing documentation
```

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Anthropic API key (required for Claude AI parsing)
- ERPNext instance (optional, for ERP integration features)

### Setup Steps

1. **Clone or download the repository**

```bash
cd InvoicePOParser
```

2. **Create a virtual environment (recommended)**

```bash
python -m venv venv

# On Windows (Git Bash)
source venv/Scripts/activate

# On Windows (CMD)
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

### Claude AI Setup (Required)

1. **Get your Anthropic API key** from [Anthropic Console](https://console.anthropic.com/settings/keys)

2. **Create `.anthropickey` file** in project root:

```bash
echo "sk-ant-api03-your-actual-key-here" > .anthropickey
```

⚠️ **Never commit `.anthropickey` to version control!**

### ERPNext Setup (Optional, for ERP Integration)

1. **Copy the environment template**

```bash
cp .env.example .env
```

2. **Edit `.env` file** with your ERPNext credentials:

```bash
ERPNEXT_URL=http://localhost:8080
ERPNEXT_API_KEY=your_api_key_here
ERPNEXT_API_SECRET=your_api_secret_here
```

3. **Generate ERPNext API credentials**:
   - Log in to ERPNext
   - Go to: User → API Access → Generate Keys
   - Copy the API Key and API Secret to your `.env` file

⚠️ **Never commit `.env` to version control!**

📖 For detailed ERPNext integration setup, see [ERPNEXT_QUICKSTART.md](ERPNEXT_QUICKSTART.md)

## 🚀 Running the API

Start the API server using `uvicorn`:

**From the project root directory:**

```bash
python -m uvicorn app.main:app --reload --port 8000
```

Or using the virtual environment Python explicitly:

```bash
venv/Scripts/python.exe -m uvicorn app.main:app --reload --port 8000
```

The API will be available at: **http://localhost:8000**

- API Documentation (Swagger UI): http://localhost:8000/docs
- Alternative Documentation (ReDoc): http://localhost:8000/redoc

## 📡 API Endpoints

### Core Endpoints

### 1. **Health Check**

```bash
GET /
GET /health
```

**Response:**
```json
{
  "message": "DocIntelligenceAPI with ERPNext Integration is running",
  "version": "2.0.0",
  "endpoints": {
    "documents": "/upload/invoice, /upload/po, /supported-types",
    "erpnext": "/erpnext/test-connection, /erpnext/company, /erpnext/supplier, /erpnext/customer, /erpnext/item, /erpnext/purchase-order, /erpnext/sales-invoice"
  }
}
```

### Document Parsing Endpoints

### 2. **Get Supported Document Types**

```bash
GET /supported-types
```

**Response:**
```json
{
  "supported_types": ["invoice", "po", "purchase_order"]
}
```

### 3. **Upload and Parse Invoice**

```bash
POST /upload/invoice
```

**Parameters:**
- `file` (required): PDF file to parse

**Example using curl:**

```bash
curl -X POST "http://localhost:8000/upload/invoice" \
  -F "file=@path/to/invoice.pdf"
```

**Response Format:**

```json
{
  "confidence": 0.85,
  "data": {
    "InvoiceId": "12345",
    "VendorName": "Vendor Company Name",
    "InvoiceDate": "2024-01-15",
    "BillingAddressRecipient": "Customer Name",
    "ShippingAddress": "123 Main St, City, Country",
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

### 4. **Upload and Parse Purchase Order**

```bash
POST /upload/po
```

**Parameters:**
- `file` (required): PDF file to parse

**Example using curl:**

```bash
curl -X POST "http://localhost:8000/upload/po" \
  -F "file=@path/to/purchase_order.pdf"
```

**Response Format:**

```json
{
  "po_number": "PO-000X",
  "date": "2024-01-24",
  "supplier_name": "Supplier Company Name",
  "company_name": "Buyer Company Name",
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

### 5. **Test ERPNext Connection**

```bash
GET /erpnext/test-connection
```

**Response:**
```json
{
  "connected": true,
  "message": "Successfully connected to ERPNext"
}
```

### 6. **Get Company Details**

```bash
GET /erpnext/company/{company_name}
```

**Example:**
```bash
curl -X GET "http://localhost:8000/erpnext/company/My%20Company"
```

**Response:**
```json
{
  "name": "My Company",
  "abbr": "MC",
  "default_currency": "USD",
  ...
}
```

### 7. **Get Supplier Details**

```bash
GET /erpnext/supplier/{supplier_name}
```

**Example:**
```bash
curl -X GET "http://localhost:8000/erpnext/supplier/ABC%20Supplies"
```

### 8. **Get Customer Details**

```bash
GET /erpnext/customer/{customer_name}
```

### 9. **Get Item Details**

```bash
GET /erpnext/item/{item_code}
```

### 10. **Submit Purchase Order to ERPNext**

```bash
POST /erpnext/purchase-order
```

**Request Body:**
```json
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

**Response:**
```json
{
  "success": true,
  "message": "Purchase Order PO-00001 created and submitted successfully",
  "po_name": "PO-00001",
  "details": { ... }
}
```

### 11. **Submit Sales Invoice to ERPNext**

```bash
POST /erpnext/sales-invoice
```

**Request Body:**
```json
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

**Response:**
```json
{
  "success": true,
  "message": "Sales Invoice SINV-00001 created and submitted successfully",
  "invoice_name": "SINV-00001",
  "details": { ... }
}
```

📖 For detailed ERPNext endpoint documentation and workflows, see [ERPNEXT_QUICKSTART.md](ERPNEXT_QUICKSTART.md)

## 🏗️ Architecture & Design

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     UI Application                           │
│              (React/Vue/Angular/etc.)                        │
└───────────────┬─────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Backend (Port 8000)                 │
│                                                              │
│  ┌──────────────────────┐    ┌──────────────────────────┐  │
│  │  Documents Router    │    │   ERPNext Router         │  │
│  │  /upload/invoice     │    │   /erpnext/*             │  │
│  │  /upload/po          │    │                          │  │
│  └──────────┬───────────┘    └──────────┬───────────────┘  │
│             │                            │                   │
│             ▼                            ▼                   │
│  ┌──────────────────────┐    ┌──────────────────────────┐  │
│  │  Parser Factory      │    │  ERPNext Workflows       │  │
│  │  Claude Parsers      │    │  - Purchase Order        │  │
│  └──────────┬───────────┘    │  - Sales Invoice         │  │
│             │                 └──────────┬───────────────┘  │
│             ▼                            │                   │
│  ┌──────────────────────┐               │                   │
│  │  Claude AI Service   │               │                   │
│  │  (Document Parsing)  │               │                   │
│  └──────────────────────┘               │                   │
│                                          ▼                   │
│                              ┌──────────────────────────┐   │
│                              │  ERPNext Service         │   │
│                              │  (API Client)            │   │
│                              └──────────┬───────────────┘   │
└─────────────────────────────────────────┼───────────────────┘
                                          │
                                          ▼
                              ┌──────────────────────────┐
                              │   ERPNext ERP System     │
                              │   (Port 8080)            │
                              └──────────────────────────┘
```

### Architecture Highlights

1. **Modular Router Design**: Separate routers for document processing and ERPNext integration
2. **Middleware Layer**: API acts as intelligent middleware between UI and ERPNext
3. **Automated Workflows**: Complete end-to-end workflows with validation and entity creation
4. **Service Isolation**: Clear separation between Claude AI parsing and ERPNext integration
5. **Configuration Management**: Centralized config for ERPNext credentials and endpoints

### OOP Design

#### Documents Module

```
┌─────────────────────────────────────────────────────────────┐
│                    ParserFactory                             │
│                   parser_factory.py                          │
│  - Routes to appropriate Claude parser based on doc type    │
│  - Manages singleton ClaudeService instance                 │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│              Claude AI Parsers                               │
│                                                              │
│  InvoiceClaudeParser  │  PurchaseOrderClaudeParser          │
│                                                              │
│  ↓ inherits from                                            │
│  BaseClaudeParser (Abstract Base Class)                     │
│  - get_prompt()                                             │
│  - validate_schema()                                        │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    ClaudeService                             │
│                 services/claude_service.py                   │
│  - Claude API integration (claude-3-5-sonnet-20241022)      │
│  - PDF → base64 encoding                                     │
│  - JSON parsing and validation                               │
└─────────────────────────────────────────────────────────────┘
```

#### ERPNext Integration Module

```
┌─────────────────────────────────────────────────────────────┐
│                    ERPNext Workflows                         │
│               workflows/erpnext_workflows.py                 │
│  - submit_purchase_order_workflow()                         │
│  - submit_sales_invoice_workflow()                          │
│  - Entity validation and auto-creation                      │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    ERPNext Service                           │
│                services/erpnext_service.py                   │
│  - api_request(): Generic API client                        │
│  - get_entity(): Fetch entities from ERPNext                │
│  - create_entity(): Create new entities                     │
│  - update_entity(): Update existing entities                │
│  - ensure_entity_exists(): Validation + auto-creation       │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                   ERPNext Config                             │
│               config/erpnext_config.py                       │
│  - Credential management (API key, secret)                  │
│  - URL configuration                                        │
│  - Header generation for authentication                     │
└─────────────────────────────────────────────────────────────┘
```

### OOP Design Principles

1. **Abstract Base Class**
   - `BaseClaudeParser`: Claude AI parser interface with `get_prompt()`, `validate_schema()`, and `parse()`

2. **Concrete Implementations**
   - `InvoiceClaudeParser`: AI-powered invoice extraction with confidence scoring
   - `PurchaseOrderClaudeParser`: AI-powered PO extraction with field validation

3. **Factory Pattern (`ParserFactory`)**
   - Intelligent routing based on document type
   - Returns appropriate Claude parser instance
   - Manages singleton ClaudeService instance
   - Supports: "invoice", "po", "purchase_order"

4. **Service Layer**
   - `ClaudeService`: Centralized Claude API integration
   - `ERPNextService`: ERPNext REST API client with error handling
   - API key management via `.anthropickey` and `.env` files
   - PDF encoding and JSON parsing utilities

5. **Workflow Pattern (`ERPNextWorkflows`)**
   - Complete end-to-end workflows for Purchase Orders and Sales Invoices
   - Entity validation and auto-creation (Supplier, Customer, Item)
   - Error handling and rollback support
   - Status tracking and reporting

6. **Configuration Management**
   - `prompts.py`: Versioned, centralized Claude AI prompt templates
   - `erpnext_config.py`: ERPNext credentials and URL management
   - Environment variable loading with `python-dotenv`
   - Easy configuration updates without code changes

7. **Separation of Concerns**
   - Parsing logic separate from API routing
   - ERPNext integration separate from document parsing
   - Service layer separate from business logic
   - Routers separate from workflows
   - Comprehensive error handling at each layer
   - Temporary file cleanup in finally blocks

### Parsing Strategy

**Claude AI Parser:**
- Natural language understanding via Claude 3.5 Sonnet
- Multi-language support (English, Hebrew, etc.)
- Complex layout handling
- JSON-based structured output
- Field validation and normalization
- Currency detection and normalization
- 2-5 second response time **pdfplumber**: Extract text and tables from PDFs (>=0.10.0)
- **PyPDF2**: Alternative PDF processing library (>=3.0.0)
- **pydantic**: Data validation and settings management (>=2.0.0)
- **python-multipart**: Form data parsing (>=0.0.6)

### Claude AI Integration
- **anthropic**: Anthropic Python SDK for Claude API (>=0.18.0)
- **pyyaml**: YAML parsing for structured output (>=6.0.1)

### Testing
- **pytest**: Testing framework (>=7.4.0)
- **pytest-asyncio**: Async test support (>=0.21.0)
- **httpx**: HTTP client for testing (>=0.24.0
## 📝 JSON Output Schema

### Invoice Output

```json
{
  "confidence": 0.85,
  "data": {
    "InvoiceId": "string",
    "VendorName": "string",
    "InvoiceDate": "string (YYYY-MM-DD)",
    "BillingAddressRecipient": "string or null",
    "ShippingAddress": "string or null",
    "SubTotal": "float",
    "ShippingCost": "float",
    "InvoiceTotal": "float",
    "Tax": "float or null",
    "Currency": "string (ISO 4217 code: USD, EUR, ILS, GBP, etc.)",
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

### Purchase Order Output

```json
{
  "po_number": "string",
  "date": "string (YYYY-MM-DD)",
  "supplier_name": "string",
  "company_name": "string",
  "delivery_date": "string (YYYY-MM-DD)",
  "total_amount": "float",
  "currency": "string (ISO 4217 code: USD, EUR, ILS, GBP, etc.)",
  "status": "string (e.g., Pending, Approved)",
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

### Field Descriptions

**Invoice Fields:**
- `InvoiceId`: Invoice number/identifier
- `VendorName`: Vendor/supplier company name
- `InvoiceDate`: Invoice date in YYYY-MM-DD format
- `BillingAddressRecipient`: Billing address recipient name (nullable)
- `ShippingAddress`: Shipping address (nullable)
- `SubTotal`: Subtotal amount (number only, no currency symbol)
- `ShippingCost`: Shipping/delivery cost (number only)
- `InvoiceTotal`: Total invoice amount including all charges
- `Tax`: Tax amount (nullable if not specified)
- `Currency`: ISO 4217 currency code (USD, EUR, ILS, GBP, etc.)
- `Items`: Array of line items (can be empty)
- `confidence`: Overall confidence score (0.0-1.0)
- `predictionTime`: Time taken to parse the document in seconds

**Purchase Order Fields:**
- `po_number`: Purchase order number/identifier
- `date`: PO issue date in YYYY-MM-DD format
- `supplier_name`: Supplier company name
- `company_name`: Buyer company name (issuer of PO)
- `delivery_date`: Expected delivery date in YYYY-MM-DD format
- `total_amount`: Total order amount (number only)
- `currency`: ISO 4217 currency code (USD, EUR, ILS, GBP, etc.)
- `status`: Order status (e.g., Pending, Approved, Completed)
- `items`: Array of ordered items

**Currency Support:**
- Automatically detects and normalizes currency symbols ($, €, ₪, £, ¥, ₹)
- Returns ISO 4217 standard codes (USD, EUR, ILS, GBP, JPY, INR)
- Defaults to USD if currency cannot be determined

## 🔧 Configuration

- **Upload Directory**: `tmp/uploads/` (automatically created)
- **Default Port**: 8000
- **Log Level**: INFO
- **Claude Model**: claude-3-5-sonnet-20241022
- **API Key File**: `.anthropickey` (must be in project root)

## 🛡️ Error Handling

The API provides meaningful error responses:

- **400 Bad Request**: Invalid file type or parsing errors
- **404 Not Found**: File not found
- **500 Internal Server Error**: Unexpected server errors

All errors are logged with detailed information for debugging.

## 🧪 Testing

### Test API Endpoints

Run the unit tests:

```bash
pytest tests/test_api.py -v
```

### Test Claude Parsers Standalone

Test Claude parsers directly without starting the API server:

```bash
# From the tests directory
python tests/test_claude_parsers.py invoice path/to/invoice.pdf
python tests/test_claude_parsers.py po path/to/purchase_order.pdf
```

This allows you to test parsing functionality independently and see detailed output.

## 🚀 Future Enhancements

This API is designed to be extensible for:

- ✅ **Multilingual Support**: Already supported via Claude AI
- ✅ **ML-based Extraction**: Integrated via Claude AI
- ✅ **Currency Detection**: Implemented with ISO 4217 normalization
- ✅ **ERPNext Integration**: Complete Purchase Order and Sales Invoice workflows
- 📦 **Batch Processing**: Upload and parse multiple documents at once
- 📊 **Database Integration**: Store parsed data locally for caching and analytics
- 🎯 **Field-level Confidence**: Return confidence for each individual field from Claude
- 📈 **Analytics Dashboard**: Track parsing performance and accuracy
- 🔐 **Authentication**: Add API key or OAuth2 authentication for production
- 💾 **Caching**: Cache parsed results by PDF hash to reduce API costs
- 📄 **Additional Document Types**: Support for receipts, bills of lading, etc.
- 🔄 **Webhook Support**: Real-time notifications for ERPNext document status changes

## 📄 Dependencies

### Web Framework
- **fastapi**: Modern web framework for building APIs (>=2.0.0)
- **uvicorn[standard]**: ASGI server for running FastAPI (>=0.23.0)
- **python-multipart**: Form data parsing (>=0.0.6)

### ERPNext Integration
- **requests**: HTTP client for ERPNext API (>=2.31.0)
- **python-dotenv**: Environment variable management (>=1.0.0)

### PDF Processing
- **pdfplumber**: Extract text and tables from PDFs (>=0.10.0)
- **PyPDF2**: Alternative PDF processing library (>=3.0.0)

### Data Validation
- **pydantic**: Data validation and settings management (>=2.0.0)

### Claude AI Integration
- **anthropic**: Anthropic Python SDK for Claude API (>=0.18.0)
- **pyyaml**: YAML parsing for structured output (>=6.0.1)

### Testing
- **pytest**: Testing framework (>=7.4.0)
- **pytest-asyncio**: Async test support (>=0.21.0)
- **httpx**: HTTP client for testing (>=0.24.0)

## 🤝 Contributing

This is a production-ready backend API with ERPNext integration. To extend functionality:

**For Document Parsing:**
1. Add new parser classes inheriting from `BaseClaudeParser`
2. Add prompts to `config/prompts.py`
3. Update `ParserFactory` to support new document types
4. Add corresponding endpoints in `app/routers/documents.py`
5. Write unit tests for new parsers

**For ERPNext Integration:**
1. Add new workflow functions in `app/workflows/erpnext_workflows.py`
2. Extend `ERPNextService` with new API methods if needed
3. Add new endpoints in `app/routers/erpnext.py`
4. Update configuration in `app/config/erpnext_config.py` if needed
5. Write integration tests in `tests/integration/`

## 📚 Additional Documentation

- **[ERPNEXT_QUICKSTART.md](ERPNEXT_QUICKSTART.md)**: Complete ERPNext integration guide
- **[TEST_DOCUMENTATION.md](TEST_DOCUMENTATION.md)**: Testing strategies and examples
- **Swagger UI**: http://localhost:8000/docs (when server is running)

## 📞 Support

For issues or questions, please review the code documentation and inline comments. All classes and methods include comprehensive docstrings.

## 📜 License

This project is designed for internal use as a document parsing API.

---

**Built with ❤️ using FastAPI, Claude AI, ERPNext, and Python**

**Version 2.0.0** - Now with ERPNext ERP Integration

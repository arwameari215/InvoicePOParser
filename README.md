# DocIntelligenceAPI

A standalone Python backend API for parsing **Invoices** and **Purchase Orders (POs)** from PDF files. Built with FastAPI and following OOP principles, this API extracts structured data from documents using **Claude AI** with confidence scoring and clean JSON output.

## 🚀 Features

- ✅ **FastAPI** backend with RESTful endpoints
- ✅ **Claude AI Integration** - Intelligent document parsing using Claude 3.5 Sonnet
- ✅ **OOP-based architecture** with abstract base classes and concrete implementations
- ✅ **PDF parsing** using `pdfplumber` for text extraction
- ✅ **Factory Pattern** for parser selection with intelligent routing
- ✅ **Multi-language support** - English, Hebrew, and more via Claude AI
- ✅ **Currency extraction** - Detects and normalizes currency codes (USD, EUR, ILS, etc.)
- ✅ **Confidence scoring** for extracted fields (OCI-like output for invoices)
- ✅ **Type hints and docstrings** throughout the codebase
- ✅ **Comprehensive logging** for debugging and monitoring
- ✅ **Unit tests** with mocked data
- ✅ **Production-ready** error handling
- ✅ **Modular and extensible** design for future enhancements

## 📁 Project Structure

```
InvoicePOParser/
├── app/
│   ├── main.py                          # FastAPI entrypoint
│   ├── parser_factory.py                # Factory for Claude parser selection
│   ├── config/
│   │   └── prompts.py                   # Versioned Claude AI prompts
│   ├── services/
│   │   └── claude_service.py            # Claude API integration
│   ├── parsers/
│   │   ├── base_claude_parser.py        # Abstract Claude parser interface
│   │   ├── invoice_claude_parser.py     # Claude AI invoice parser ✨
│   │   └── po_claude_parser.py          # Claude AI PO parser ✨
│   ├── utils/
│   │   └── pdf_loader.py                # PDF loading utilities
│   └── tmp/uploads/                     # Temporary file upload directory
├── tests/
│   ├── test_api.py                      # API endpoint tests
│   └── test_claude_parsers.py           # Standalone Claude parser tests
├── .anthropickey                        # Your Anthropic API key (create this)
├── .anthropickey.example                # API key template
├── .gitignore                           # Git ignore rules
├── venv/                                # Virtual environment
├── requirements.txt                     # Python dependencies
└── README.md                            # This file
```

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Anthropic API key (required for Claude AI parsing)

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

### 1. **Health Check**

```bash
GET /
GET /health
```

**Response:**
```json
{
  "message": "DocIntelligenceAPI is running",
  "version": "1.0.0",
  "endpoints": "/upload/invoice, /upload/po"
}
```

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
```## 🏗️ Architecture & Design

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        FastAPI API                           │
│                         main.py                              │
│           POST /upload/invoice                               │
│           POST /upload/po                                    │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
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
   - API key management via `.anthropickey` file
   - PDF encoding and JSON parsing utilities

5. **Configuration Management**
   - `prompts.py`: Versioned, centralized prompt templates
   - Easy prompt updates without code changes

6. **Separation of Concerns**
   - Parsing logic separate from API logic
   - Service layer separate from parsers
   - Prompts separate from parsing logic
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
- 📦 **Batch Processing**: Upload and parse multiple documents at once
- 📊 **Database Integration**: Store parsed invoice data in database
- 🎯 **Field-level Confidence**: Return confidence for each individual field from Claude
- 📈 **Analytics Dashboard**: Track parsing performance and accuracy
- 🔐 **Authentication**: Add API key or OAuth2 authentication
- 💾 **Caching**: Cache parsed results by PDF hash

## 📄 Dependencies

### Web Framework
- **fastapi**: Modern web framework for building APIs (>=0.100.0)
- **uvicorn[standard]**: ASGI server for running FastAPI (>=0.23.0)
- **python-multipart**: Form data parsing (>=0.0.6)

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

This is a production-ready, standalone backend API. To extend functionality:

1. Add new parser classes inheriting from `BaseClaudeParser`
2. Add prompts to `config/prompts.py`
3. Update `ParserFactory` to support new document types
4. Add corresponding endpoints in `main.py`
5. Write unit tests for new features

## 📞 Support

For issues or questions, please review the code documentation and inline comments. All classes and methods include comprehensive docstrings.

## 📜 License

This project is designed for internal use as a document parsing API.

---

**Built with ❤️ using FastAPI, Claude AI, and Python**

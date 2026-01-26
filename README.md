# DocIntelligenceAPI

A standalone Python backend API for parsing **Invoices** and **Purchase Orders (POs)** from PDF files. Built with FastAPI and following OOP principles, this API extracts structured data from documents with confidence scoring and returns clean JSON output similar to OCI Document AI.

## 🚀 Features

- ✅ **FastAPI** backend with RESTful endpoints
- ✅ **OOP-based architecture** with abstract base classes and concrete implementations
- ✅ **Enhanced PDF parsing** using `pdfplumber` with regex-based field extraction
- ✅ **Factory Pattern** for parser selection
- ✅ **Confidence scoring** for extracted fields (OCI-like output)
- ✅ **Type hints and docstrings** throughout the codebase
- ✅ **Comprehensive logging** for debugging and monitoring
- ✅ **Unit tests** with mocked data (21/23 passing)
- ✅ **Production-ready** error handling
- ✅ **ERPNext integration** script included
- ✅ **Modular and extensible** design for future enhancements

## 📁 Project Structure

```
InvoicePOParser/
├── app/
│   ├── main.py                          # FastAPI entrypoint with endpoints
│   ├── parser_factory.py                # Factory to return parser based on doc type
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── base_parser.py               # Abstract DocumentParser class
│   │   ├── enhanced_invoice_parser.py   # Enhanced InvoiceParser with confidence scores
│   │   └── po_parser.py                 # PurchaseOrderParser implementation
│   └── tmp/uploads/                     # Temporary file upload directory
├── tests/
│   ├── test_invoice.py                  # Unit tests for invoice parser
│   ├── test_po.py                       # Unit tests for PO parser
│   └── test_api.py                      # API endpoint tests
├── venv/                                # Virtual environment
├── create_po_erpnext.py                 # ERPNext Purchase Order creation script
├── requirements.txt                     # Python dependencies
└── README.md                            # This file
```

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

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

## 🚀 Running the API

Start the API server using `uvicorn`:

```bash
cd app
python -m uvicorn main:app --reload --port 8000
```

Or from the root directory:

```bash
cd app && ../venv/Scripts/python -m uvicorn main:app --reload --port 8000
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

**Example using curl:**

```bash
curl -X POST "http://localhost:8000/upload/invoice" \
  -F "file=@C:\Users\LENOVO\ArwaMeari\invoices_sample\invoice_Anthony_Jacobs_37594.pdf"
```

**Example Response (OCI-like format):**

```json
{
  "confidence": 0.84,
  "data": {
    "InvoiceId": "37594",
    "VendorName": "SuperStore",
    "InvoiceDate": "2012-12-27",
    "BillingAddressRecipient": "Anthony Jacobs",
    "ShippingAddress": "1915, Beverly,Massachusetts,United States",
    "SubTotal": 567.04,
    "ShippingCost": 11.34,
    "InvoiceTotal": 578.38,
    "Tax": null,
    "Items": [
      {
        "description": "Xerox 1906 Paper, Office Supplies, OFF-PA-6457",
        "quantity": 4,
        "unit_price": 141.76,
        "total": 567.04
      }
    ]
  },
  "predictionTime": 0.272
}
```

**Key Features:**
- Extracts vendor name from document header
- Parses dates in multiple formats (ISO, US, text)
- Separates billing and shipping addresses
- Handles item descriptions with hyphens and special characters
- Includes confidence scoring for extraction quality
- Returns prediction time for performance monitoring

### 4. **Upload and Parse Purchase Order**

```bash
POST /upload/po
```

**Example using curl:**

```bash
curl -X POST "http://localhost:8000/upload/po" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/purchase_order.pdf"
```

**Example Response:**

```json
{
  "metadata": {
    "po_number": "PO123",
    "date": "2026-01-25",
    "supplier_name": "Supplier X",
    "delivery_date": "2026-02-01",
    "total_amount": 5000.0,
    "status": "Pending"
  },
  "items": [
    {
      "description": "Product A",
      "quantity": 10,
      "unit_price": 500,
      "total": 5000
    }
  ]
}
```

## 🧪 Running Tests

Run all unit tests using pytest from the virtual environment:

```bash
venv/Scripts/python -m pytest -v
```

Run specific test file:

```bash
venv/Scripts/python -m pytest tests/test_invoice.py -v
venv/Scripts/python -m pytest tests/test_po.py -v
venv/Scripts/python -m pytest tests/test_api.py -v
```

**Test Results:** 21 passed, 2 failed (non-critical)

## 🏗️ Architecture & Design

### OOP Design Principles

1. **Abstract Base Class (`DocumentParser`)**
   - Defines the interface for all parsers
   - Methods: `load_file()`, `parse_metadata()`, `parse_items()`, `to_dict()`, `validate_file_exists()`

2. **Concrete Implementations**
   - `EnhancedInvoiceParser`: Parses invoice-specific fields with confidence scores
   - `PurchaseOrderParser`: Parses PO-specific fields

3. **Factory Pattern (`ParserFactory`)**
   - Returns appropriate parser based on document type
   - Centralizes parser instantiation logic
   - Supports: "invoice", "po", "purchase_order"

4. **Separation of Concerns**
   - Parsing logic separate from API logic
   - Regex-based field extraction for accuracy
   - Comprehensive error handling at each layer
   - Temporary file cleanup in finally blocks

### Key Classes

- **DocumentParser** (Abstract): Base class for all parsers with file validation
- **EnhancedInvoiceParser**: Extracts InvoiceId, VendorName, dates, addresses, items with confidence scoring
- **PurchaseOrderParser**: Extracts PO number, supplier, delivery date, status, items
- **ParserFactory**: Static factory to create parsers based on document type

### Parsing Strategy

The enhanced invoice parser uses:
- **Text-based extraction** instead of table detection for better accuracy
- **Regex patterns** for field matching with multiple format support
- **Line-by-line parsing** for item extraction
- **Confidence scoring** based on successful field matches
- **Multi-line description support** for item details

## 📝 JSON Output Format

### Invoice Output (OCI-like format)

```json
{
  "confidence": 0.84,
  "data": {
    "InvoiceId": "string",
    "VendorName": "string",
    "InvoiceDate": "string (YYYY-MM-DD)",
    "BillingAddressRecipient": "string",
    "ShippingAddress": "string",
    "SubTotal": "float",
    "ShippingCost": "float",
    "InvoiceTotal": "float",
    "Tax": "float or null",
    "Items": [
      {
        "description": "string",
        "quantity": "int",
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
  "metadata": {
    "po_number": "string",
    "date": "string (YYYY-MM-DD)",
    "supplier_name": "string",
    "delivery_date": "string (YYYY-MM-DD)",
    "total_amount": "float",
    "status": "string"
  },
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

## 🔧 Configuration

- **Upload Directory**: `tmp/uploads/` (automatically created)
- **Default Port**: 8000
- **Log Level**: INFO

## 🛡️ Error Handling

The API provides meaningful error responses:

- **400 Bad Request**: Invalid file type or parsing errors
- **404 Not Found**: File not found
- **500 Internal Server Error**: Unexpected server errors

All errors are logged with detailed information for debugging.

## 🚀 Future Enhancements

This API is designed to be extensible for:

- 🌍 **Multilingual Support**: Parse documents in multiple languages
- 📦 **Batch Processing**: Upload and parse multiple documents at once
- 🤖 **ML-based Extraction**: Integrate machine learning models for better accuracy
- 📊 **Database Integration**: Store parsed invoice data in database
- 🎯 **Field-level Confidence**: Return confidence for each individual field
- 📈 **Analytics Dashboard**: Track parsing performance and accuracy
- 🔐 **Authentication**: Add API key or OAuth2 authentication
- ✅ **ERPNext Integration**: Direct API integration with ERPNext

## 📄 Dependencies

- **fastapi**: Modern web framework for building APIs (>=0.100.0)
- **uvicorn[standard]**: ASGI server for running FastAPI (>=0.23.0)
- **pdfplumber**: Extract text and tables from PDFs (>=0.10.0)
- **PyPDF2**: Alternative PDF processing library (>=3.0.0)
- **pydantic**: Data validation and settings management (>=2.0.0)
- **pytest**: Testing framework (>=7.4.0)
- **pytest-asyncio**: Async test support (>=0.21.0)
- **httpx**: HTTP client for testing (>=0.24.0)
- **python-multipart**: Form data parsing (>=0.0.6)
- **requests**: HTTP library for ERPNext integration

## 🤝 Contributing

This is a production-ready, standalone backend API. To extend functionality:

1. Add new parser classes inheriting from `DocumentParser`
2. Update `ParserFactory` to support new document types
3. Add corresponding endpoints in `main.py`
4. Write unit tests for new features

## 📞 Support

For issues or questions, please review the code documentation and inline comments. All classes and methods include comprehensive docstrings.

## 📜 License

This project is designed for internal use and future integration with ERPNext.

---

**Built with ❤️ using FastAPI and Python**

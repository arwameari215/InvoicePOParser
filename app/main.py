"""
DocIntelligenceAPI - FastAPI backend for parsing invoices and purchase orders.

This API provides endpoints to upload and parse PDF documents (invoices and POs)
and returns structured JSON data.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any
import os
import sys
import logging
import shutil
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parser_factory import ParserFactory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="DocIntelligenceAPI",
    description="API for parsing Invoices and Purchase Orders from PDF files",
    version="1.0.0"
)

# Create upload directory if it doesn't exist
UPLOAD_DIR = Path("tmp/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/")
async def root() -> Dict[str, str]:
    """
    Root endpoint - API health check.
    
    Returns:
        Dict[str, str]: Welcome message and API status.
    """
    return {
        "message": "DocIntelligenceAPI is running",
        "version": "1.0.0",
        "endpoints": "/upload/invoice, /upload/po"
    }


@app.post("/upload/invoice")
async def upload_invoice(file: UploadFile = File(...)) -> JSONResponse:
    """
    Upload and parse an invoice PDF file.
    
    Args:
        file (UploadFile): The invoice PDF file to parse.
    
    Returns:
        JSONResponse: Parsed invoice data in JSON format with metadata and items.
    
    Raises:
        HTTPException: If file type is invalid or parsing fails.
    """
    logger.info(f"Received invoice upload request: {file.filename}")
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        logger.error(f"Invalid file type: {file.filename}")
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only PDF files are supported."
        )
    
    # Save uploaded file
    file_path = None
    try:
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"File saved to: {file_path}")
        
        # Parse the invoice
        parser = ParserFactory.get_parser("invoice", str(file_path))
        parser.load_file()
        result = parser.to_dict()
        
        logger.info(f"Successfully parsed invoice: {file.filename}")
        return JSONResponse(content=result, status_code=200)
    
    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    
    except ValueError as e:
        logger.error(f"Parsing error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Parsing error: {str(e)}")
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    finally:
        # Clean up uploaded file
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Cleaned up temporary file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to remove temporary file: {str(e)}")


@app.post("/upload/invoice/enhanced")
async def upload_invoice_enhanced(file: UploadFile = File(...)) -> JSONResponse:
    """
    Upload and parse an invoice PDF file with enhanced extraction and confidence scores.
    
    Returns OCI-like structured response with:
    - confidence: Overall document confidence score
    - data: Extracted fields (InvoiceId, VendorName, InvoiceDate, Items, etc.)
    - dataConfidence: Confidence score for each field
    - predictionTime: Processing time in seconds
    
    Args:
        file (UploadFile): The invoice PDF file to parse.
    
    Returns:
        JSONResponse: Enhanced parsed invoice data with confidence scores.
    
    Raises:
        HTTPException: If file type is invalid or parsing fails.
    """
    logger.info(f"Received enhanced invoice upload request: {file.filename}")
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        logger.error(f"Invalid file type: {file.filename}")
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only PDF files are supported."
        )
    
    # Save uploaded file
    file_path = None
    try:
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"File saved to: {file_path}")
        
        # Parse with enhanced parser
        parser = ParserFactory.get_parser("invoice_enhanced", str(file_path))
        parser.load_file()
        result = parser.to_dict()
        
        logger.info(f"Successfully parsed enhanced invoice: {file.filename}")
        return JSONResponse(content=result, status_code=200)
    
    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    
    except ValueError as e:
        logger.error(f"Parsing error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Parsing error: {str(e)}")
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    finally:
        # Clean up uploaded file
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Cleaned up temporary file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to remove temporary file: {str(e)}")


@app.post("/upload/po")
async def upload_po(file: UploadFile = File(...)) -> JSONResponse:
    """
    Upload and parse a Purchase Order PDF file.
    
    Args:
        file (UploadFile): The PO PDF file to parse.
    
    Returns:
        JSONResponse: Parsed PO data in JSON format with metadata and items.
    
    Raises:
        HTTPException: If file type is invalid or parsing fails.
    """
    logger.info(f"Received PO upload request: {file.filename}")
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        logger.error(f"Invalid file type: {file.filename}")
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only PDF files are supported."
        )
    
    # Save uploaded file
    file_path = None
    try:
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"File saved to: {file_path}")
        
        # Parse the PO
        parser = ParserFactory.get_parser("po", str(file_path))
        parser.load_file()
        result = parser.to_dict()
        
        logger.info(f"Successfully parsed PO: {file.filename}")
        return JSONResponse(content=result, status_code=200)
    
    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    
    except ValueError as e:
        logger.error(f"Parsing error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Parsing error: {str(e)}")
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    finally:
        # Clean up uploaded file
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Cleaned up temporary file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to remove temporary file: {str(e)}")


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.
    
    Returns:
        Dict[str, str]: API health status.
    """
    return {"status": "healthy", "service": "DocIntelligenceAPI"}


@app.get("/supported-types")
async def get_supported_types() -> Dict[str, list]:
    """
    Get list of supported document types.
    
    Returns:
        Dict[str, list]: List of supported document types.
    """
    return {"supported_types": ParserFactory.get_supported_types()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

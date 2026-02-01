"""
Document Processing Router

Handles PDF upload and parsing endpoints for invoices and purchase orders.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import logging
import shutil
from pathlib import Path

from app.parser_factory import ParserFactory


logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="", tags=["Document Processing"])

# Upload directory
UPLOAD_DIR = Path("tmp/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload/invoice")
async def upload_invoice(file: UploadFile = File(...)) -> JSONResponse:
    """
    Upload and parse an invoice PDF file using Claude AI.
    
    Args:
        file (UploadFile): The invoice PDF file to parse.
    
    Returns:
        JSONResponse: Parsed invoice data.
    
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
        
        # Parse the invoice with Claude AI
        parser = ParserFactory.get_parser("invoice", str(file_path))
        result = parser.parse()
        
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


@router.post("/upload/po")
async def upload_po(file: UploadFile = File(...)) -> JSONResponse:
    """
    Upload and parse a Purchase Order PDF file using Claude AI.
    
    Args:
        file (UploadFile): The PO PDF file to parse.
    
    Returns:
        JSONResponse: Parsed PO data.
    
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
        
        # Parse the PO with Claude AI
        parser = ParserFactory.get_parser("po", str(file_path))
        result = parser.parse()
        
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


@router.get("/supported-types")
async def get_supported_types() -> dict:
    """
    Get list of supported document types.
    
    Returns:
        dict: List of supported document types.
    """
    return {"supported_types": ParserFactory.get_supported_types()}

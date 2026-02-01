"""
DocIntelligenceAPI - FastAPI backend for parsing invoices and purchase orders.

This API provides endpoints to upload and parse PDF documents (invoices and POs)
and returns structured JSON data with ERPNext integration.
"""

from fastapi import FastAPI
from typing import Dict
import sys
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="DocIntelligenceAPI",
    description="API for parsing Invoices and Purchase Orders from PDF files with ERPNext integration",
    version="2.0.0"
)

# Import and include routers (after app initialization to handle import errors gracefully)
try:
    from app.routers import documents, erpnext
    app.include_router(documents.router)
    app.include_router(erpnext.router)
    logger.info("✅ Successfully loaded all routers")
except Exception as e:
    logger.warning(f"⚠️ Could not load some routers: {str(e)}")
    # API will still work with just root/health endpoints


@app.get("/")
async def root() -> Dict[str, str]:
    """
    Root endpoint - API health check.
    
    Returns:
        Dict[str, str]: Welcome message and API status.
    """
    return {
        "message": "DocIntelligenceAPI is running",
        "version": "2.0.0",
        "status": "healthy",
        "endpoints": {
            "documents": "/upload/invoice, /upload/po, /supported-types",
            "erpnext": "/erpnext/test-connection, /erpnext/purchase-order, /erpnext/sales-invoice",
            "docs": "/docs, /redoc"
        }
    }


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.
    
    Returns:
        Dict[str, str]: API health status.
    """
    return {"status": "healthy", "service": "DocIntelligenceAPI"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



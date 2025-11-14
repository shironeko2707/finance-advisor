import os
import tempfile
from typing import List
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import aiofiles

from auto_report.main import main
import warnings

warnings.filterwarnings("ignore")  # This ignores all warnings


app = FastAPI(title="Auto Report API", description="API for generating reports from templates and documents")

@app.post("/generate-report")
async def generate_report(
    template: UploadFile = File(..., description="Excel template file"),
    documents: List[UploadFile] = File(..., description="Document files to process")
):
    """
    Generate a report using the provided template and documents.
    
    Args:
        template: Excel template file (.xlsx)
        documents: List of document files (PDF, etc.)
    
    Returns:
        The generated report file
    """
    if not template.filename.endswith(('.xlsx', '.xls', '.xlsm')):
        raise HTTPException(status_code=400, detail="Template must be an Excel file (.xlsx, .xls or .xlsm)")
    
    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp()
        
        template_path = os.path.join(temp_dir, template.filename)
        async with aiofiles.open(template_path, 'wb') as f:
            content = await template.read()
            await f.write(content)
        
        document_paths = []
        for doc in documents:
            doc_path = os.path.join(temp_dir, doc.filename)
            async with aiofiles.open(doc_path, 'wb') as f:
                content = await doc.read()
                await f.write(content)
            document_paths.append(doc_path)
        
        output_path = await main(template_path, document_paths)
        
        if not output_path:
            raise HTTPException(
                status_code=422, 
                detail="No tables found in the uploaded documents. Please upload documents containing tables for processing."
            )
        
        return FileResponse(
            path=output_path,
            filename=f"report_{template.filename}",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")
    
    finally:
        if temp_dir and os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

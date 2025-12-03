"""
Exports Routes
"""
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
import io
import csv

router = APIRouter(prefix="/api/exports", tags=["Exports"])


@router.get("/{format}")
async def export_data(format: str):
    """
    Export data in specified format
    """
    if format not in ["excel", "pdf", "csv"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Format '{format}' not supported. Use: excel, pdf, or csv"
        )
    
    # Por ahora, retornar CSV demo
    if format == "csv":
        # Crear CSV en memoria
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Producto", "Ventas", "Cantidad"])
        writer.writerow(["Producto A", "4530000", "8765"])
        writer.writerow(["Producto B", "3890000", "7543"])
        writer.writerow(["Producto C", "3210000", "6234"])
        
        output.seek(0)
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=export.csv"}
        )
    
    # Para otros formatos, retornar mensaje
    return {
        "message": f"Export {format} functionality coming soon",
        "format": format
    }

"""
Filters Routes
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/filters", tags=["Filters"])

DEMO_FILTERS = {
    "countries": ["Perú", "México", "Colombia", "Ecuador"],
    "sellers": ["Vendedor 1", "Vendedor 2", "Vendedor 3", "Vendedor 4", "Vendedor 5"],
    "products": ["Producto A", "Producto B", "Producto C", "Producto D", "Producto E"],
    "date_range": {
        "min_date": "2023-01-01",
        "max_date": "2024-12-31"
    }
}


@router.get("/options")
async def get_filter_options():
    """
    Get available filter options
    """
    return DEMO_FILTERS

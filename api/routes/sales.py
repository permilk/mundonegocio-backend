"""
Sales Routes - Con datos de demostración
"""
from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from datetime import datetime, timedelta
import random

router = APIRouter(prefix="/api/sales", tags=["Sales"])

# Datos demo
DEMO_DATA = {
    "summary": {
        "total_sales": 22650000.00,
        "total_orders": 43886,
        "avg_ticket": 516.25,
        "unique_customers": 8234
    },
    "by_period": [
        {"date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"), 
         "sales": random.randint(2000000, 4000000),
         "orders": random.randint(5000, 7000)}
        for i in range(7)
    ],
    "top_products": [
        {"product": "Producto A", "sales": 4530000, "quantity": 8765},
        {"product": "Producto B", "sales": 3890000, "quantity": 7543},
        {"product": "Producto C", "sales": 3210000, "quantity": 6234},
        {"product": "Producto D", "sales": 2890000, "quantity": 5432},
        {"product": "Producto E", "sales": 2450000, "quantity": 4765}
    ],
    "by_seller": [
        {"seller": "Vendedor 1", "sales": 5430000, "orders": 10543},
        {"seller": "Vendedor 2", "sales": 4890000, "orders": 9234},
        {"seller": "Vendedor 3", "sales": 3210000, "orders": 6789},
        {"seller": "Vendedor 4", "sales": 2890000, "orders": 5678},
        {"seller": "Vendedor 5", "sales": 2450000, "orders": 4876}
    ]
}


@router.get("/summary")
async def get_sales_summary(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    seller: Optional[str] = Query(None)
):
    """
    Get sales summary
    """
    return DEMO_DATA["summary"]


@router.get("/by-period")
async def get_sales_by_period(
    period: str = Query("daily", regex="^(daily|weekly|monthly)$"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """
    Get sales by period
    """
    return DEMO_DATA["by_period"]


@router.get("/top-products")
async def get_top_products(
    limit: int = Query(5, ge=1, le=50),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """
    Get top products
    """
    return DEMO_DATA["top_products"][:limit]


@router.get("/by-seller")
async def get_sales_by_seller(
    limit: int = Query(5, ge=1, le=50),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """
    Get sales by seller
    """
    return DEMO_DATA["by_seller"][:limit]

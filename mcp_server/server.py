from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.controllers.vehicle_controller import VehicleController
from mcp_server.schemas import VehicleSearchRequest, VehicleResponse
from typing import List

app = FastAPI(title="MCP Vehicle Server")


@app.post("/search", response_model=List[VehicleResponse])
async def search_vehicles(
    request: VehicleSearchRequest,
    db: Session = Depends(get_db)
):
    """Busca de veículos com filtros estruturados."""
    vehicles = VehicleController.search_vehicles(
        db=db,
        marca=request.marca,
        modelo=request.modelo,
        ano_min=request.ano_min,
        ano_max=request.ano_max,
        combustivel=request.combustivel,
        preco_min=request.preco_min,
        preco_max=request.preco_max,
        transmissao=request.transmissao,
        limit=request.limit
    )
    return vehicles


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

from pydantic import BaseModel, field_validator
from typing import Optional, List, Union


class VehicleSearchRequest(BaseModel):
    marca: Optional[Union[str, List[str]]] = None
    modelo: Optional[Union[str, List[str]]] = None
    ano_min: Optional[int] = None
    ano_max: Optional[int] = None
    combustivel: Optional[Union[str, List[str]]] = None
    preco_min: Optional[float] = None
    preco_max: Optional[float] = None
    transmissao: Optional[Union[str, List[str]]] = None
    limit: int = 10

    @field_validator('marca', 'modelo', 'combustivel', 'transmissao', mode='before')
    @classmethod
    def normalize_to_string(cls, v):
        """Converte listas para a primeira string, se necessário."""
        if isinstance(v, list) and len(v) > 0:
            return v[0]
        return v


class VehicleResponse(BaseModel):
    id: int
    marca: str
    modelo: str
    ano: int
    cor: str
    quilometragem: int
    preco: float
    combustivel: str
    transmissao: str

    class Config:
        from_attributes = True

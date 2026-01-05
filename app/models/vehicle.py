from sqlalchemy import Column, Integer, String, Float, Enum
from app.database import Base
import enum


class FuelType(str, enum.Enum):
    GASOLINA = "Gasolina"
    ETANOL = "Etanol"
    FLEX = "Flex"
    DIESEL = "Diesel"
    ELETRICO = "Elétrico"
    HIBRIDO = "Híbrido"


class TransmissionType(str, enum.Enum):
    MANUAL = "Manual"
    AUTOMATICA = "Automática"
    CVT = "CVT"
    AUTOMATIZADA = "Automatizada"


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    marca = Column(String(50), nullable=False, index=True)
    modelo = Column(String(100), nullable=False)
    ano = Column(Integer, nullable=False, index=True)
    motorizacao = Column(String(20), nullable=False)
    combustivel = Column(Enum(FuelType), nullable=False, index=True)
    cor = Column(String(30), nullable=False)
    quilometragem = Column(Integer, nullable=False)
    portas = Column(Integer, nullable=False)
    transmissao = Column(Enum(TransmissionType), nullable=False)
    preco = Column(Float, nullable=False, index=True)
    proprietarios = Column(Integer, default=1)
    placa = Column(String(10), unique=True)

from sqlalchemy.orm import Session
from app.models.vehicle import Vehicle
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class VehicleController:
    """Controller para operações de busca de veículos."""

    @staticmethod
    def search_vehicles(
        db: Session,
        marca: Optional[str] = None,
        modelo: Optional[str] = None,
        ano_min: Optional[int] = None,
        ano_max: Optional[int] = None,
        combustivel: Optional[str] = None,
        preco_min: Optional[float] = None,
        preco_max: Optional[float] = None,
        transmissao: Optional[str] = None,
        limit: int = 10
    ) -> List[Vehicle]:
        """Busca veículos no banco de dados com filtros estruturados.

        Args:
            db: Sessão do banco de dados
            marca: Marca do veículo (busca parcial, case-insensitive)
            modelo: Modelo do veículo (busca parcial, case-insensitive)
            ano_min: Ano mínimo (inclusivo)
            ano_max: Ano máximo (inclusivo)
            combustivel: Tipo de combustível (exato)
            preco_min: Preço mínimo (inclusivo)
            preco_max: Preço máximo (inclusivo)
            transmissao: Tipo de transmissão (exato)
            limit: Número máximo de resultados (padrão: 10, máx: 100)

        Returns:
            Lista de veículos que correspondem aos filtros

        Raises:
            ValueError: Se parâmetros inválidos forem fornecidos

        Nota: Se usuário fornecer min > max (ex: ano_min=2020, ano_max=2015),
        os valores são automaticamente corrigidos (swapped). Ver CHANGELOG.
        """
        # Validação de limit
        if limit <= 0:
            logger.warning(f"Limit inválido: {limit}. Usando padrão 10.")
            limit = 10
        if limit > 100:
            logger.warning(f"Limit muito alto: {limit}. Limitando a 100.")
            limit = 100

        # Validação e correção de ranges
        if ano_min is not None and ano_max is not None and ano_min > ano_max:
            logger.warning(f"ano_min ({ano_min}) > ano_max ({ano_max}). Corrigindo automaticamente.")
            ano_min, ano_max = ano_max, ano_min

        if preco_min is not None and preco_max is not None and preco_min > preco_max:
            logger.warning(f"preco_min ({preco_min}) > preco_max ({preco_max}). Corrigindo automaticamente.")
            preco_min, preco_max = preco_max, preco_min

        # Validação de anos (não pode ser negativo ou muito futuro)
        current_year = 2026
        if ano_min is not None and (ano_min < 1900 or ano_min > current_year + 1):
            logger.warning(f"ano_min fora do range válido: {ano_min}")
            raise ValueError(f"ano_min deve estar entre 1900 e {current_year + 1}")

        if ano_max is not None and (ano_max < 1900 or ano_max > current_year + 1):
            logger.warning(f"ano_max fora do range válido: {ano_max}")
            raise ValueError(f"ano_max deve estar entre 1900 e {current_year + 1}")

        # Validação de preços (não pode ser negativo)
        if preco_min is not None and preco_min < 0:
            logger.warning(f"preco_min negativo: {preco_min}")
            raise ValueError("preco_min não pode ser negativo")

        if preco_max is not None and preco_max < 0:
            logger.warning(f"preco_max negativo: {preco_max}")
            raise ValueError("preco_max não pode ser negativo")

        # Log dos filtros aplicados
        filters_applied = {
            "marca": marca,
            "modelo": modelo,
            "ano_min": ano_min,
            "ano_max": ano_max,
            "combustivel": combustivel,
            "preco_min": preco_min,
            "preco_max": preco_max,
            "transmissao": transmissao,
            "limit": limit
        }
        active_filters = {k: v for k, v in filters_applied.items() if v is not None}
        logger.info(f"Buscando veículos com filtros: {active_filters}")

        # Construção da query
        query = db.query(Vehicle)

        if marca:
            query = query.filter(Vehicle.marca.ilike(f"%{marca}%"))
        if modelo:
            query = query.filter(Vehicle.modelo.ilike(f"%{modelo}%"))
        if ano_min:
            query = query.filter(Vehicle.ano >= ano_min)
        if ano_max:
            query = query.filter(Vehicle.ano <= ano_max)
        if combustivel:
            query = query.filter(Vehicle.combustivel == combustivel)
        if preco_min:
            query = query.filter(Vehicle.preco >= preco_min)
        if preco_max:
            query = query.filter(Vehicle.preco <= preco_max)
        if transmissao:
            query = query.filter(Vehicle.transmissao == transmissao)

        results = query.limit(limit).all()
        logger.info(f"Encontrados {len(results)} veículos")

        return results

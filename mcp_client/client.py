import httpx
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class MCPClient:
    """Cliente para comunicação com o servidor MCP."""
    def __init__(self, server_url: str = "http://localhost:8000"):
        """Inicializa o cliente MCP.

        Args:
            server_url: URL do servidor MCP (padrão: http://localhost:8000)
        """
        self.server_url = server_url
        logger.info(f"MCPClient inicializado: {server_url}")

    async def search_vehicles(self, filters: Dict[str, Any]) -> List[Dict]:
        """Busca veículos via servidor MCP.

        Args:
            filters: Dicionário com filtros de busca

        Returns:
            Lista de veículos encontrados

        Raises:
            httpx.HTTPStatusError: Se o servidor retornar erro HTTP
            httpx.TimeoutException: Se a requisição exceder timeout
            httpx.RequestError: Se houver erro de conexão
        """
        logger.info(f"Buscando veículos com filtros: {filters}")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.server_url}/search",
                    json=filters,
                    timeout=30.0
                )
                response.raise_for_status()
                results = response.json()
                logger.info(f"Servidor retornou {len(results)} veículos")
                return results

        except httpx.TimeoutException as e:
            logger.error(f"Timeout ao buscar veículos: {e}")
            raise

        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP ao buscar veículos: {e.response.status_code}")
            raise

        except httpx.RequestError as e:
            logger.error(f"Erro de conexão ao buscar veículos: {e}")
            raise

    async def health_check(self) -> Dict:
        """Verifica saúde do servidor MCP.

        Returns:
            Dicionário com status do servidor

        Raises:
            httpx.HTTPStatusError: Se o servidor retornar erro HTTP
            httpx.TimeoutException: Se a requisição exceder timeout
            httpx.RequestError: Se houver erro de conexão
        """
        logger.debug("Verificando saúde do servidor MCP")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.server_url}/health",
                    timeout=10.0
                )
                response.raise_for_status()
                health_data = response.json()
                logger.info(f"Health check: {health_data}")
                return health_data

        except httpx.TimeoutException as e:
            logger.error(f"Timeout no health check: {e}")
            raise

        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP no health check: {e.response.status_code}")
            raise

        except httpx.RequestError as e:
            logger.error(f"Erro de conexão no health check: {e}")
            raise

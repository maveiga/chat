import asyncio
import logging
import threading
import time
import uvicorn
from agent.agent import VehicleAgent
from mcp_client.client import MCPClient
from app.views.vehicle_view import VehicleView
from app.config import MCP_SERVER_HOST, MCP_SERVER_PORT, OPENAI_API_KEY

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
# Silenciar logs verbosos de bibliotecas
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def start_mcp_server():
    """Inicia o servidor FastAPI em background usando threading."""
    print("Iniciando servidor MCP")
    logger.info("Iniciando servidor FastAPI")

    def run_server():
        """Função que roda o uvicorn em thread separada."""
        uvicorn.run(
            "mcp_server.server:app",
            host=MCP_SERVER_HOST,
            port=MCP_SERVER_PORT,
            log_level="error"
        )

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    print("Aguardando servidor inicializar...")
    time.sleep(3)

    print(f"Servidor MCP rodando em http://{MCP_SERVER_HOST}:{MCP_SERVER_PORT}")
    logger.info("Servidor MCP iniciado com sucesso")


async def main():
    """Ponto de entrada principal da aplicação terminal."""
    logger.info("Iniciando sistema de busca de veículos")

    # Iniciar servidor MCP em background
    start_mcp_server()

    print()
    print("=" * 60)
    print("BEM-VINDO AO SISTEMA DE BUSCA DE VEÍCULOS")
    print("=" * 60)
    print()

    try:
        logger.info("Inicializando agente e cliente MCP")
        agent = VehicleAgent(api_key=OPENAI_API_KEY)
        mcp_client = MCPClient()

        initial_response = agent.chat("Olá")
        print(f"Agente: {initial_response}\n")

        while True:
            try:
                user_input = input("Você: ").strip()

                if user_input.lower() in ["sair", "exit", "quit"]:
                    logger.info("Usuário encerrou a sessão")
                    print("\nAté logo!")
                    break

                if not user_input:
                    logger.debug("Entrada vazia, ignorando")
                    continue

                # Obter resposta do agente
                logger.debug(f"Usuário: {user_input[:50]}...")
                agent_response = agent.chat(user_input)
                print(f"\nAgente: {agent_response}\n")

                # Verificar se deve executar busca
                if agent.should_search(agent_response):
                    logger.info("Executando busca de veículos")
                    print("Buscando veículos...\n")

                    filters = agent.extract_filters()

                    vehicles = await mcp_client.search_vehicles(filters)
                    logger.info(f"Encontrados {len(vehicles)} veículos")

                    # Se não encontrou e tem ano específico, expande ±3 anos
                    if len(vehicles) == 0 and 'ano_min' in filters and 'ano_max' in filters:
                        if filters['ano_min'] == filters['ano_max']:  # Ano específico
                            ano_original = filters['ano_min']
                            filters['ano_min'] = ano_original - 3
                            filters['ano_max'] = ano_original + 3

                            print(f"Nenhum veículo encontrado em {ano_original}.")
                            print(f"Buscando entre {filters['ano_min']} e {filters['ano_max']}...\n")

                            vehicles = await mcp_client.search_vehicles(filters)
                            logger.info(f"Busca expandida: encontrados {len(vehicles)} veículos")

                    formatted_results = VehicleView.format_results(vehicles)
                    print(formatted_results)

                    followup = "Mostrei os resultados acima. Deseja refinar a busca?"
                    print(f"Agente: {followup}\n")

            except ValueError as e:
                logger.warning(f"Erro de validação: {e}")
                print(f"\nErro: {e}\n")

            except KeyboardInterrupt:
                logger.info("Interrupção por teclado (Ctrl+C)")
                print("\n\nAté logo!")
                break

            except Exception as e:
                logger.error(f"Erro inesperado no loop: {e}", exc_info=True)
                print(f"\nErro inesperado: {e}")
                print("Por favor, tente novamente.\n")

    except Exception as e:
        logger.critical(f"Erro fatal ao inicializar aplicação: {e}", exc_info=True)
        print(f"\nErro fatal: {e}")
        print("Não foi possível iniciar o sistema. Verifique os logs.\n")
        return 1

    logger.info("Sistema encerrado normalmente")
    return 0


if __name__ == "__main__":
    asyncio.run(main())




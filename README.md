# Sistema de Busca de Veículos com Agente Conversacional

Sistema de busca de veículos usando agente conversacional (LangChain + OpenAI) que se comunica via protocolo MCP com servidor FastAPI e banco SQLite.

## Stack Tecnológica

- Python 3.11+
- FastAPI (servidor MCP)
- SQLite (banco de dados)
- LangChain + OpenAI GPT-4 (agente conversacional)
- SQLAlchemy (ORM)

## Instalação

### 1. Ambiente virtual e dependências

```bash
# Criar e ativar ambiente virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente

```bash
# Copiar .env.example para .env
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# Editar .env e adicionar OPENAI_API_KEY
```

### 3. Popular banco de dados

```bash
python scripts/seed_database.py
```

### 4. Iniciar aplicação

```bash
python main.py
```

O servidor MCP inicia automaticamente em background!

## Testes

```bash
pytest -v
```

## Estrutura do Projeto

```
├── app/                 # Core (models, controllers, views)
├── mcp_server/         # Servidor FastAPI (endpoints)
├── mcp_client/         # Cliente HTTP
├── agent/              # Agente conversacional (LangChain)
├── scripts/            # Scripts (seed, init_db)
├── tests/              # 21 testes automatizados
└── main.py             # Ponto de entrada
```

## Arquitetura

```
Terminal → Agente → MCP Client → MCP Server → SQLite
```

1. Usuário conversa com agente
2. Agente extrai filtros (marca, modelo, preço, etc)
3. Cliente envia para servidor via HTTP
4. Servidor consulta banco SQLite
5. Resultados retornam formatados

## Exemplos de Uso

```
Você: quero um gol até 50 mil
Agente: Vou buscar um Volkswagen Gol até R$ 50.000. Um momento...

Encontrei 5 veículo(s):
1. Volkswagen Gol (2019) - R$ 42,500.00
...
```

## Comandos Úteis

```bash
# Ver dados do banco
sqlite3 vehicles.db "SELECT * FROM vehicles LIMIT 10;"

# Resetar banco
rm vehicles.db
python scripts/seed_database.py

# Testar API manualmente
curl http://localhost:8000/health
```

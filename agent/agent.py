from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from agent.prompts import SYSTEM_PROMPT, EXTRACTION_PROMPT
import json
import logging
from typing import List, Dict

# Configure logging
logger = logging.getLogger(__name__)


class VehicleAgent:
    """Agente conversacional para busca de veículos.

    Usa LangChain + OpenAI, extrair filtros de busca.
    """

    # Filtros válidos aceitos pela API de busca
    VALID_FILTERS = {
        "marca", "modelo", "ano_min", "ano_max", "combustivel",
        "preco_min", "preco_max", "transmissao", "cor", "quilometragem_max"
    }

    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            api_key=api_key
        )
        self.conversation_history: List = [SystemMessage(content=SYSTEM_PROMPT)]

    def chat(self, user_message: str) -> str:
        """Processa mensagem e retorna resposta do agente."""
        if not user_message or not user_message.strip():
            raise ValueError("Mensagem do usuário não pode estar vazia")

        try:
            self.conversation_history.append(HumanMessage(content=user_message))
            response = self.llm.invoke(self.conversation_history)
            self.conversation_history.append(AIMessage(content=response.content))
            return response.content

        except Exception as e:
            # Reverte histórico se deu erro
            if self.conversation_history and isinstance(self.conversation_history[-1], HumanMessage):
                self.conversation_history.pop()
            raise

    def extract_filters(self) -> Dict:
        """Extrai filtros da conversa (marca, modelo, preço, etc).

        Retorna dict vazio se o LLM não retornar JSON válido.
        """
        recent_messages = [
            msg for msg in self.conversation_history
            if not isinstance(msg, SystemMessage)
        ][-6:]

        conversation_text = "\n".join([
            f"{'User' if isinstance(msg, HumanMessage) else 'Agent'}: {msg.content}"
            for msg in recent_messages
        ])

        prompt = EXTRACTION_PROMPT.format(conversation=conversation_text)

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])

            # Remove markdown code fence se existir
            content = response.content.strip()
            if content.startswith("```"):

                content = content.split("\n", 1)[1]
                content = content.rsplit("\n```", 1)[0]
                content = content.strip()

            filters = json.loads(content)

            # Remove filtros inválidos
            invalid_keys = set(filters.keys()) - self.VALID_FILTERS
            if invalid_keys:
                filters = {k: v for k, v in filters.items() if k in self.VALID_FILTERS}

            return filters

        except json.JSONDecodeError:
            return {}
        except Exception:
            return {}

    def should_search(self, agent_response: str) -> bool:
        """Detecta se agente quer executar busca (baseado em keywords)."""
        response_lower = agent_response.lower()
        search_phrases = [
            "vou buscar", "vou procurar", "vou encontrar",
            "deixa eu buscar", "deixa eu procurar",
            "irei buscar", "irei procurar",
            "vamos buscar", "vamos procurar"
        ]

        if any(phrase in response_lower for phrase in search_phrases):
            return True

        keywords = ["buscar", "procurar", "encontrar", "mostrar veículos", "mostrar carros"]
        question_indicators = ["?", "posso", "devo", "poderia", "gostaria"]

        has_keyword = any(keyword in response_lower for keyword in keywords)
        is_question = any(ind in response_lower for ind in question_indicators)

        # Evita falso positivo: "Posso buscar por marca?" (pergunta, não ação)
        if has_keyword and is_question:
            return False

        return has_keyword

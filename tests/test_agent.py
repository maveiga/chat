import pytest
from agent.agent import VehicleAgent


@pytest.fixture
def agent():
    return VehicleAgent(api_key="fake-key-for-testing")


def test_agent_initialization(agent):
    assert len(agent.conversation_history) == 1


def test_should_search_detection(agent):
    assert agent.should_search("Vou buscar os veículos agora")
    assert not agent.should_search("Qual sua marca preferida?")

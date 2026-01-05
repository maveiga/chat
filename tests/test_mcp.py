import pytest
from app.controllers.vehicle_controller import VehicleController
from app.database import SessionLocal


@pytest.fixture
def db_session():
    """Fixture para sessão de banco de dados."""
    session = SessionLocal()
    yield session
    session.close()


#TESTES DE BUSCA BÁSICA

def test_search_by_marca(db_session):
    """Testa busca por marca exata."""
    results = VehicleController.search_vehicles(db_session, marca="Toyota")
    assert len(results) > 0
    assert all(v.marca == "Toyota" for v in results)


def test_search_by_marca_partial(db_session):
    """Testa busca parcial por marca"""
    results = VehicleController.search_vehicles(db_session, marca="toy")
    assert len(results) > 0
    assert all("toy" in v.marca.lower() for v in results)


def test_search_by_price_range(db_session):
    """Testa busca por faixa de preço."""
    results = VehicleController.search_vehicles(
        db_session,
        preco_min=30000,
        preco_max=50000
    )
    assert all(30000 <= v.preco <= 50000 for v in results)


def test_search_by_year_range(db_session):
    """Testa busca por faixa de anos."""
    results = VehicleController.search_vehicles(
        db_session,
        ano_min=2015,
        ano_max=2020
    )
    assert all(2015 <= v.ano <= 2020 for v in results)


def test_search_multiple_filters(db_session):
    """Testa busca com múltiplos filtros combinados."""
    results = VehicleController.search_vehicles(
        db_session,
        marca="Toyota",
        ano_min=2018,
        preco_max=100000
    )
    assert all(v.marca == "Toyota" for v in results)
    assert all(v.ano >= 2018 for v in results)
    assert all(v.preco <= 100000 for v in results)


# TESTES DE EDGE CASES

def test_search_ano_min_greater_than_max_should_swap(db_session):
    """Testa correção automática quando ano_min > ano_max.

    Edge case comum: usuário fornece valores invertidos.
    Sistema deve corrigir automaticamente (swap).
    """
    results = VehicleController.search_vehicles(
        db_session,
        ano_min=2020,
        ano_max=2015  # Invertido!
    )
    # Sistema deve corrigir e buscar entre 2015-2020
    assert all(2015 <= v.ano <= 2020 for v in results)


def test_search_preco_min_greater_than_max_should_swap(db_session):
    """Testa correção automática quando preco_min > preco_max.

    Edge case documentado no CHANGELOG: usuário pode fornecer valores invertidos.
    """
    results = VehicleController.search_vehicles(
        db_session,
        preco_min=80000,
        preco_max=50000
    )
    # Sistema deve corrigir e buscar entre 50000-80000
    assert all(50000 <= v.preco <= 80000 for v in results)


def test_search_limit_zero_should_use_default(db_session):
    """Testa que limit <= 0 usa valor padrão (10)."""
    results = VehicleController.search_vehicles(db_session, limit=0)
    assert len(results) <= 10


def test_search_limit_too_high_should_cap_at_100(db_session):
    """Testa que limit > 100 é limitado a 100."""
    results = VehicleController.search_vehicles(db_session, limit=500)
    assert len(results) <= 100


def test_search_no_filters_should_return_limited_results(db_session):
    """Testa busca sem filtros (retorna até o limit)."""
    results = VehicleController.search_vehicles(db_session)
    assert len(results) <= 10  # Limit padrão


# TESTES DE VALIDAÇÃO

def test_search_invalid_year_min_should_raise(db_session):
    """Testa que ano_min inválido levanta ValueError."""
    with pytest.raises(ValueError, match="ano_min deve estar entre"):
        VehicleController.search_vehicles(db_session, ano_min=1800)


def test_search_invalid_year_max_should_raise(db_session):
    """Testa que ano_max inválido levanta ValueError."""
    with pytest.raises(ValueError, match="ano_max deve estar entre"):
        VehicleController.search_vehicles(db_session, ano_max=2050)


def test_search_negative_price_min_should_raise(db_session):
    """Testa que preco_min negativo levanta ValueError."""
    with pytest.raises(ValueError, match="preco_min não pode ser negativo"):
        VehicleController.search_vehicles(db_session, preco_min=-1000)


def test_search_negative_price_max_should_raise(db_session):
    """Testa que preco_max negativo levanta ValueError."""
    with pytest.raises(ValueError, match="preco_max não pode ser negativo"):
        VehicleController.search_vehicles(db_session, preco_max=-500)


#TESTES DE CASOS REALISTAS

def test_search_scenario_family_car(db_session):
    """Cenário real: Família procurando carro popular até R$60k."""
    results = VehicleController.search_vehicles(
        db_session,
        preco_max=60000,
        ano_min=2018,
        limit=20
    )
    assert all(v.preco <= 60000 for v in results)
    assert all(v.ano >= 2018 for v in results)


def test_search_scenario_luxury_car(db_session):
    """Cenário real: Cliente procurando carro de luxo (BMW/Mercedes)."""
    results_bmw = VehicleController.search_vehicles(
        db_session,
        marca="BMW",
        preco_min=100000
    )
    results_mercedes = VehicleController.search_vehicles(
        db_session,
        marca="Mercedes-Benz",
        preco_min=100000
    )

    if results_bmw:
        assert all(v.marca == "BMW" for v in results_bmw)
        assert all(v.preco >= 100000 for v in results_bmw)

    if results_mercedes:
        assert all(v.marca == "Mercedes-Benz" for v in results_mercedes)
        assert all(v.preco >= 100000 for v in results_mercedes)


def test_search_scenario_new_car(db_session):
    """Cenário real: Cliente quer carro seminovo (últimos 3 anos)."""
    results = VehicleController.search_vehicles(
        db_session,
        ano_min=2021
    )
    assert all(v.ano >= 2021 for v in results)


#TESTES ADICIONAIS

def test_search_by_combustivel(db_session):
    """Testa busca por tipo de combustível."""
    results = VehicleController.search_vehicles(
        db_session,
        combustivel="Flex"
    )
    if results:
        assert all(v.combustivel == "Flex" for v in results)


def test_search_by_transmissao(db_session):
    """Testa busca por tipo de transmissão."""
    results = VehicleController.search_vehicles(
        db_session,
        transmissao="Automática"
    )
    if results:
        assert all(v.transmissao == "Automática" for v in results)


def test_search_with_all_filters(db_session):
    """Testa busca com todos os filtros simultaneamente."""
    results = VehicleController.search_vehicles(
        db_session,
        marca="Toyota",
        modelo="Corolla",
        ano_min=2015,
        ano_max=2020,
        preco_min=40000,
        preco_max=90000,
        combustivel="Flex",
        transmissao="Automática"
    )
    for v in results:
        assert v.marca == "Toyota"
        assert v.modelo == "Corolla"
        assert 2015 <= v.ano <= 2020
        assert 40000 <= v.preco <= 90000
        assert v.combustivel == "Flex"
        assert v.transmissao == "Automática"


def test_search_case_insensitive_marca(db_session):
    """Testa que busca por marca é case-insensitive."""
    results_lower = VehicleController.search_vehicles(db_session, marca="toyota")
    results_upper = VehicleController.search_vehicles(db_session, marca="TOYOTA")
    results_mixed = VehicleController.search_vehicles(db_session, marca="ToYoTa")

    assert len(results_lower) == len(results_upper) == len(results_mixed)


def test_search_partial_modelo_match(db_session):
    """Testa busca parcial por modelo."""
    results = VehicleController.search_vehicles(db_session, modelo="cor")
    if results:
        assert all("cor" in v.modelo.lower() for v in results)

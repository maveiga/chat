from faker import Faker
import random
import logging
from sqlalchemy.exc import IntegrityError
from app.database import SessionLocal
from app.models.vehicle import Vehicle, FuelType, TransmissionType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

fake = Faker('pt_BR')

MARCAS = ["Toyota", "Honda", "Ford", "Chevrolet", "Volkswagen", "Fiat",
          "Hyundai", "Nissan", "Renault", "Jeep", "BMW", "Mercedes-Benz"]

MODELOS = {
    "Toyota": ["Corolla", "Hilux", "Etios", "Yaris", "Camry", "RAV4"],
    "Honda": ["Civic", "HR-V", "City", "Fit", "Accord", "CR-V"],
    "Ford": ["Ka", "Ranger", "EcoSport", "Fusion", "Focus", "Edge"],
    "Chevrolet": ["Onix", "S10", "Tracker", "Cruze", "Spin", "Trailblazer"],
    "Volkswagen": ["Gol", "Polo", "Virtus", "T-Cross", "Tiguan", "Jetta"],
    "Fiat": ["Uno", "Argo", "Toro", "Mobi", "Pulse", "Strada"],
    "Hyundai": ["HB20", "Creta", "Tucson", "i30", "Santa Fe", "Azera"],
    "Nissan": ["Kicks", "Versa", "Frontier", "Sentra", "March", "Leaf"],
    "Renault": ["Kwid", "Sandero", "Duster", "Captur", "Oroch", "Fluence"],
    "Jeep": ["Renegade", "Compass", "Commander", "Wrangler", "Grand Cherokee"],
    "BMW": ["320i", "X1", "X3", "X5", "M3", "530i"],
    "Mercedes-Benz": ["C180", "GLA", "GLC", "A200", "E250", "S500"]
}

CORES = ["Branco", "Preto", "Prata", "Vermelho", "Azul", "Cinza", "Verde", "Dourado", "Marrom"]
MOTORIZACOES = ["1.0", "1.4", "1.6", "1.8", "2.0", "2.4", "3.0", "3.5"]


def generate_unique_plate(existing_plates: set) -> str:
    """Gera placa única (evita duplicatas)."""
    max_attempts = 100
    for _ in range(max_attempts):
        plate = fake.license_plate()
        if plate not in existing_plates:
            existing_plates.add(plate)
            return plate

    import string
    for attempt in range(max_attempts):
        letters = ''.join(random.choices(string.ascii_uppercase, k=3))
        numbers = ''.join(random.choices(string.digits, k=4))
        plate = f"{letters}-{numbers}"
        if plate not in existing_plates:
            existing_plates.add(plate)
            logger.warning(f"Usando placa customizada após {attempt} tentativas: {plate}")
            return plate

    raise ValueError("Não foi possível gerar placa única após múltiplas tentativas")


def generate_vehicle(existing_plates: set):
    """Gera veículo com dados fake + depreciação de 5% ao ano."""
    marca = random.choice(MARCAS)
    modelo = random.choice(MODELOS.get(marca, ["Modelo Padrão"]))
    ano = random.randint(2010, 2024)

    # Lógica para preços mais realistas baseados no ano Deprecia 5% por ano
    base_price = random.uniform(20000, 150000)
    age_factor = (2024 - ano) * 0.05
    price = base_price * (1 - age_factor)

    return Vehicle(
        marca=marca,
        modelo=modelo,
        ano=ano,
        motorizacao=random.choice(MOTORIZACOES),
        combustivel=random.choice(list(FuelType)),
        cor=random.choice(CORES),
        quilometragem=random.randint(0, 200000),
        portas=random.choice([2, 4, 5]),
        transmissao=random.choice(list(TransmissionType)),
        preco=round(max(price, 15000), 2),  # Mínimo R$ 15.000
        proprietarios=random.randint(1, 3),
        placa=generate_unique_plate(existing_plates)
    )


def seed_database(count=150):
    """Popula banco com N veículos fake."""
    if count <= 0:
        raise ValueError("Count deve ser maior que 0")

    if count > 1000:
        logger.warning(f"Count muito alto ({count}). Isso pode demorar.")

    db = SessionLocal()
    existing_plates = set()

    try:
        logger.info(f"Iniciando geração de {count} veículos...")

        # Verificar placas já existentes no banco
        existing_vehicles = db.query(Vehicle.placa).all()
        existing_plates = {v.placa for v in existing_vehicles}
        logger.info(f"Encontradas {len(existing_plates)} placas já no banco")

        # Gerar veículos com placas únicas
        vehicles = []
        for i in range(count):
            try:
                vehicle = generate_vehicle(existing_plates)
                vehicles.append(vehicle)

                if (i + 1) % 50 == 0:
                    logger.info(f"Gerados {i + 1}/{count} veículos...")

            except ValueError as e:
                logger.error(f"Erro ao gerar veículo {i + 1}: {e}")
                raise

        logger.info(f"Inserindo {len(vehicles)} veículos no banco...")
        db.bulk_save_objects(vehicles)
        db.commit()

        logger.info(f"{count} veículos inseridos com sucesso!")
        print(f"{count} veículos inseridos com sucesso!")

    except IntegrityError as e:
        logger.error(f"Erro de integridade ao inserir veículos: {e}", exc_info=True)
        print(f"Erro de integridade: {e}")
        db.rollback()
        raise

    except Exception as e:
        logger.error(f"Erro inesperado ao inserir veículos: {e}", exc_info=True)
        print(f"Erro ao inserir veículos: {e}")
        db.rollback()
        raise

    finally:
        db.close()
        logger.info("Sessão do banco de dados fechada")


if __name__ == "__main__":
    seed_database(150)

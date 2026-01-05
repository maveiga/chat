from app.database import engine, Base
from app.models.vehicle import Vehicle


def init_database():
    print("Criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")


if __name__ == "__main__":
    init_database()

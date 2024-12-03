from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from utils.log import logger
from sqlalchemy.exc import SQLAlchemyError

Base = declarative_base()

DATABASE_URL = "sqlite:///../cars_2.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


def initialize_database():
    try:
        Base.metadata.create_all(engine)
    except Exception as e:
        logger.error(f"Ошибка при создании таблицы: {e}")
        raise


def save_cars_to_db(cars):
    if not cars:
        return

    session = Session()
    try:
        with session.begin():
            session.add_all(cars)
    except SQLAlchemyError as e:
        logger.error(f"Ошибка сохранения данных в БД: {e}")
        session.rollback()
    finally:
        session.close()

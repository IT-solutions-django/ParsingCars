from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from utils.log import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
import pytz

Base = declarative_base()

DATABASE_URL = "sqlite:///cars_2.db"
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


novosibirsk_tz = pytz.timezone("Asia/Novosibirsk")


def get_novosibirsk_time():
    return datetime.now(novosibirsk_tz)


class Car(Base):
    __tablename__ = 'car'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_car = Column(String)
    url_car = Column(String)
    car_mark = Column(String)
    car_model = Column(String)
    car_complectation = Column(String)
    price = Column(String)
    year = Column(Integer)
    drive = Column(String)
    millage = Column(Integer)
    images = Column(String)
    main_image = Column(String)
    color = Column(String)
    transmission = Column(String)
    engine_capacity = Column(Integer)
    car_fuel = Column(String)
    car_type = Column(String)
    car_noAccident = Column(String)
    car_description = Column(String)
    created_at = Column(DateTime(timezone=True), nullable=False, default=get_novosibirsk_time)
    updated_at = Column(DateTime(timezone=True), onupdate=get_novosibirsk_time, nullable=False,
                        default=get_novosibirsk_time)


class Mark(Base):
    __tablename__ = 'mark'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)


class Model(Base):
    __tablename__ = 'model'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    mark = Column(ForeignKey('mark.id'))

from sqlalchemy import Column, Integer, String, DateTime
import requests
from datetime import datetime
from utils.log import logger
from utils.db import Base, initialize_database, Session, save_cars_to_db


class TimeDealCar(Base):
    __tablename__ = 'site_mpark_cars'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_car = Column(String)
    url_car = Column(String)
    car_name = Column(String)
    price = Column(Integer)
    year = Column(Integer)
    millage = Column(Integer)
    car_fuel = Column(String)
    car_color = Column(String)
    car_noAccident = Column(String)
    engine_capacity = Column(Integer)
    car_type = Column(String)
    transmission = Column(String)
    main_image = Column(String)
    images = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


def fetch_data_from_api(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при выполнении запроса к API: {e}")
        return None
    except ValueError as e:
        logger.error(f"Ошибка парсинга JSON: {e}")
        return None


def process_car_data(cars_list):
    cars = []
    for item in cars_list:
        try:
            id_car = item.get("demoNo")
            url_car = f"https://www.m-park.co.kr/buy/detail/{id_car}"

            session = Session()
            try:
                if not session.query(TimeDealCar).filter_by(id_car=id_car).first():
                    cars.append(
                        TimeDealCar(
                            id_car=id_car,
                            url_car=url_car
                        )
                    )
            finally:
                session.close()
        except Exception as e:
            logger.warning(f"Ошибка обработки элемента данных: {item}. Ошибка: {e}")
            continue
    return cars


def main():
    initialize_database()

    url = "https://api.m-park.co.kr/home/api/v1/wb/searchmycar/carlistinfo/get?"
    data = fetch_data_from_api(url)

    if data:
        cars_list = data.get("data", [])
        cars = process_car_data(cars_list)
        save_cars_to_db(cars)

    logger.info("Процесс обработки данных завершен.")


if __name__ == '__main__':
    main()

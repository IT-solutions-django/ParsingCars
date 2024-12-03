from bs4 import BeautifulSoup
from sqlalchemy import Column, Integer, String, DateTime
import requests
from datetime import datetime
from utils.log import logger
from utils.db import Base, initialize_database, Session, save_cars_to_db


class TimeDealCar(Base):
    __tablename__ = 'site_kbchachacha_cars'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_car = Column(String)
    url_car = Column(String)
    car_name = Column(String)
    price = Column(Integer)
    main_image = Column(String)
    images = Column(String)
    year = Column(Integer)
    millage = Column(Integer)
    color = Column(String)
    car_fuel = Column(String)
    transmission = Column(String)
    car_noAccident = Column(String)
    engine_capacity = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


def fetch_car_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при выполнении запроса к API: {e}")
        return None


def process_car_item(id_car):
    try:
        return TimeDealCar(
            id_car=id_car
        )
    except Exception as e:
        logger.warning(f"Ошибка обработки элемента данных для {id_car}. Ошибка: {e}")
        return None


def main():
    current_page = 1

    initialize_database()

    while True:
        url = f"https://www.kbchachacha.com/public/search/list.empty?page={current_page}&sort=-orderDate&_pageSize=3&pageSize=4"
        data = fetch_car_data(url)
        if not data:
            break

        try:
            soup = BeautifulSoup(data, "html.parser")
            elements = soup.find_all(attrs={"data-car-seq": True})
            data_car_seq_values = set([element["data-car-seq"] for element in elements])
            if not data_car_seq_values:
                logger.info("Данные закончились. Завершаем обработку.")
                break
        except Exception as e:
            logger.error(f"Ошибка парсинга HTML для страницы {current_page}: {e}")
            break

        cars = []
        for item in data_car_seq_values:
            car = process_car_item(item)
            if car:
                session = Session()
                try:
                    if not session.query(TimeDealCar).filter_by(id_car=car.id_car).first():
                        cars.append(car)
                finally:
                    session.close()

        save_cars_to_db(cars)
        current_page += 1

    logger.info("Процесс обработки данных завершен.")


if __name__ == '__main__':
    main()

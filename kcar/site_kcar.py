from sqlalchemy import Column, Integer, String, DateTime
import requests
from datetime import datetime
from utils.log import logger
from utils.db import Base, initialize_database, Session, save_cars_to_db


class TimeDealCar(Base):
    __tablename__ = 'site_kcar_cars'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_car = Column(String)
    url_car = Column(String)
    car_model = Column(String)
    car_mark = Column(String)
    price = Column(Integer)
    main_image = Column(String)
    images = Column(String)
    year = Column(Integer)
    millage = Column(Integer)
    drive = Column(String)
    color = Column(String)
    car_fuel = Column(String)
    transmission = Column(String)
    car_noAccident = Column(String)
    car_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


def fetch_car_data(url, headers, params):
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при выполнении запроса к API: {e}")
        return None


def process_car_item(item):
    try:
        id_car = item.get("carCd")
        car_model = item.get("modelNm")
        car_name = item.get("mnuftrNm")
        price = item.get("prc")
        image = item.get("lsizeImgPath")
        year = item.get("prdcnYr")
        millage = item.get("milg")
        color = item.get("extrColorNm")
        url_car = f"https://www.kcar.com/bc/detail/carInfoDtl?i_sCarCd={id_car}"

        return TimeDealCar(
            id_car=id_car,
            url_car=url_car,
            car_model=car_model,
            car_mark=car_name,
            price=price,
            main_image=image,
            year=year,
            millage=millage,
            color=color,
        )
    except Exception as e:
        logger.warning(f"Ошибка обработки элемента данных: {item}. Ошибка: {e}")
        return None


def main():
    url = "https://api.kcar.com/bc/timeDealCar/list"
    page_size = 28
    current_page = 1
    headers = {
        "Cookie": "ab.storage.deviceId.79570721-e48c-4ca4-b9d6-e036e9bfeff8=%7B%22g%22%3A%22b7404a2c-510b-12a8-560e-95604a58f89a%22%2C%22c%22%3A1732187811554%2C%22l%22%3A1732187811554%7D; ab.storage.sessionId.79570721-e48c-4ca4-b9d6-e036e9bfeff8=%7B%22g%22%3A%220eb30e25-7578-9663-a8fb-77a6be7f7ac7%22%2C%22e%22%3A1732190300903%2C%22c%22%3A1732187811597%2C%22l%22%3A1732188500903%7D;"
    }

    initialize_database()

    while True:
        params = {
            "currentPage": current_page,
            "pageSize": page_size,
            "creatYn": "N",
            "sIndex": 1,
            "eIndex": 10,
        }

        data = fetch_car_data(url, headers, params)
        if not data:
            break

        cars_list = data.get("data", {}).get("list", [])
        if not cars_list:
            logger.info("Данные закончились. Завершаем обработку.")
            break

        cars = []
        for item in cars_list:
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

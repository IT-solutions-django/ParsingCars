from sqlalchemy import Column, Integer, String, DateTime
from utils.request_api import fetch_page_data
from utils.log import logger
from bs4 import BeautifulSoup
import re
from datetime import datetime
from utils.db import Base, initialize_database, Session, save_cars_to_db


class TimeDealCar(Base):
    __tablename__ = 'site_bobaedream_cars'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_car = Column(String, nullable=False)
    url_car = Column(String, nullable=False)
    car_name = Column(String, nullable=False)
    engine_type = Column(String, nullable=False)
    power = Column(String, nullable=False)
    drive = Column(String, nullable=False)
    price = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    millage = Column(Integer, nullable=False)
    images = Column(String, nullable=False)
    main_image = Column(String, nullable=False)
    color = Column(String, nullable=True)
    transmission = Column(String, nullable=True)
    engine_capacity = Column(String, nullable=True)
    car_fuel = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


def parse_car_data(item):
    try:
        name = item.select_one(".tit.ellipsis a").get_text(strip=True)
        engine_type = item.select(".data-item")[1].get_text(strip=True)
        power = item.select(".data-item")[2].get_text(strip=True)
        drive = item.select(".data-item")[4].get_text(strip=True)
        year = item.select_one(".mode-cell.year .text").get_text(strip=True)
        mileage = item.select_one(".mode-cell.km .text").get_text(strip=True)
        price = item.select_one(".mode-cell.price .price-whole").get_text(strip=True)
        photo_url = f"https:{item.select_one('.thumb img')['src']}"
        car_link = item.select_one(".tit.ellipsis a")["href"]

        car_id_match = re.search(r'no=(\d+)', car_link)
        car_id = car_id_match.group(1) if car_id_match else None
        url_car = f"https://www.bobaedream.co.kr/cyber/CyberCar_view.php?no={car_id}&gubun=I"

        return TimeDealCar(
            id_car=car_id,
            url_car=url_car,
            car_name=name,
            price=price,
            year=year,
            millage=mileage,
            power=power,
            drive=drive,
            engine_type=engine_type,
            images=photo_url,
            main_image=photo_url
        )
    except Exception:
        return None


def process_cars():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.70 Safari/537.36',
        'Referer': 'https://www.bobaedream.co.kr/cyber/CyberCar.php?sel_m_gubun=ALL'
    }
    page = 1

    while True:
        data = fetch_page_data(page, headers)
        if not data:
            break

        try:
            soup = BeautifulSoup(data["myvecTxt"], "html.parser")
            items = soup.select("li.product-item")
            if not items:
                logger.info("Данные закончились. Завершаем обработку.")
                break
        except Exception as e:
            logger.error(f"Ошибка парсинга HTML для страницы {page}: {e}")
            break

        cars = []
        for item in items:
            car = parse_car_data(item)
            if car:
                session = Session()
                try:
                    if not session.query(TimeDealCar).filter_by(id_car=car.id_car).first():
                        cars.append(car)
                finally:
                    session.close()

        save_cars_to_db(cars)
        page += 1

    logger.info("Процесс обработки данных завершен.")


def main():
    initialize_database()
    process_cars()


if __name__ == '__main__':
    main()

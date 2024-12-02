import logging
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

logging.basicConfig(
    filename="../app.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

Base = declarative_base()


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


DATABASE_URL = "sqlite:///cars_2.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


def initialize_database():
    try:
        Base.metadata.create_all(engine)
    except Exception as e:
        logger.error(f"Ошибка при создании таблицы: {e}")
        raise


def fetch_page_data(page, headers):
    url = f"https://www.bobaedream.co.kr/mycar/proc/ajax_contents.php?sel_m_gubun=ALL&page={page}&order=S11&view_size=70&dummy=1732848489318"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при выполнении запроса к API для page {page}: {e}")
        return None


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


def save_cars_to_database(cars):
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

        save_cars_to_database(cars)
        page += 1

    logger.info("Процесс обработки данных завершен.")


def main():
    initialize_database()
    process_cars()


if __name__ == '__main__':
    main()

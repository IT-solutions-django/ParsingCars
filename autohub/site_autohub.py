from sqlalchemy import Column, Integer, String, DateTime
from utils.request_api import fetch_post_page_data
from utils.log import logger
from bs4 import BeautifulSoup
from datetime import datetime
from utils.db import Base, initialize_database, Session, save_cars_to_db
from urllib.parse import parse_qs, urlparse
import requests


class TimeDealCar(Base):
    __tablename__ = 'site_autohub_cars'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_car = Column(String)
    url_car = Column(String)
    car_name = Column(String)
    price = Column(String)
    year = Column(Integer)
    millage = Column(Integer)
    images = Column(String)
    main_image = Column(String)
    color = Column(String)
    transmission = Column(String)
    engine_capacity = Column(String)
    car_fuel = Column(String)
    car_description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


def fetch_page(url, id_car):
    try:
        response = requests.get(url)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при выполнении запроса к API для {id_car}: {e}")
        return None


def fetch_car_detail_dop(id_car):
    url = f"http://www.autohub.co.kr/buy/detailView.asp?DemoNo={id_car}"
    html = fetch_page(url, id_car)
    soup = BeautifulSoup(html, 'html.parser')

    info_detail = soup.select_one('.info-detail')
    if info_detail:
        engine_capacity = info_detail.find("dt", string="배기량").find_next_sibling("dd").text
    else:
        engine_capacity = None

    return engine_capacity


def parse_car_data(item):
    try:
        url_car = "www.autohub.co.kr" + item['onclick'].split("'")[1]

        parsed_url = urlparse(url_car)
        query_params = parse_qs(parsed_url.query)
        car_id = query_params.get('DemoNo', [None])[0]

        car_name_tag = item.select_one('.car-name em b')
        car_name = car_name_tag.get_text(strip=True) if car_name_tag else None

        car_price_tag = item.select_one('.car-price b')
        car_price = car_price_tag.get_text(strip=True) if car_price_tag else None

        car_description_tag = item.select_one('.car-name span')
        car_description = car_description_tag.get_text(strip=True) if car_description_tag else None

        year_tag = item.select_one('.car-state dt:-soup-contains("연식") + dd')
        millage_tag = item.select_one('.car-state dt:-soup-contains("주행거리") + dd')

        year = year_tag.get_text(strip=True) if year_tag else None
        millage = millage_tag.get_text(strip=True) if millage_tag else None

        color_tag = item.select_one('.car-data dt:-soup-contains("색상") + dd')
        car_fuel_tag = item.select_one('.car-data dt:-soup-contains("연료") + dd')
        transmission_tag = item.select_one('.car-data dt:-soup-contains("변속기") + dd')

        color = color_tag.get_text(strip=True) if color_tag else None
        car_fuel = car_fuel_tag.get_text(strip=True) if car_fuel_tag else None
        transmission = transmission_tag.get_text(strip=True) if transmission_tag else None

        images_tag = item.select('.file-image p[style]')
        images_list = [
            img['style'].split("url('")[1].split("')")[0]
            for img in images_tag if "background-image" in img['style']
        ]

        main_image = images_list[0]
        images = ", ".join(images_list)

        engine_capacity = fetch_car_detail_dop(car_id)

        return TimeDealCar(
            id_car=car_id,
            url_car=url_car,
            car_name=car_name,
            price=car_price,
            year=year,
            millage=millage,
            images=images,
            main_image=main_image,
            engine_capacity=engine_capacity,
            color=color,
            car_fuel=car_fuel,
            transmission=transmission,
            car_description=car_description

        )
    except Exception as e:
        return None


def process_cars():
    page = 1
    url = "http://www.autohub.co.kr/buy/proc/carList_proc.asp?"

    while True:
        data_post = {
            "gotoPage": page
        }
        data = fetch_post_page_data(url, data_post, page)
        if not data:
            break

        try:
            soup = BeautifulSoup(data, 'html.parser')
            elements = soup.find_all('li', onclick=True)
            if not elements:
                logger.info("Данные закончились. Завершаем обработку.")
                break
        except Exception as e:
            logger.error(f"Ошибка парсинга HTML для страницы {page}: {e}")
            break

        cars = []
        for item in elements:
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

import requests
import logging
from bs4 import BeautifulSoup
from bobaedream.site_bobaedream import Session, TimeDealCar

logging.basicConfig(
    filename="../app.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def fetch_car_details(id_car):
    url = f"https://www.bobaedream.co.kr/cyber/CyberCar_view.php?no={id_car}&gubun=I"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при выполнении запроса к API для {id_car}: {e}")
        return None


def parse_car_details(html):
    soup = BeautifulSoup(html, "html.parser")
    try:
        table = soup.find("div", class_="info-basic").find("table")

        color = extract_table_value(table, "색상")
        transmission = extract_table_value(table, "변속기")
        engine_capacity = extract_table_value(table, "배기량")
        car_fuel = extract_table_value(table, "연료")

        return color, transmission, engine_capacity, car_fuel
    except AttributeError:
        logger.warning("Не удалось найти таблицу с информацией о машине.")
        return None, None, None, None


def extract_table_value(table, field_name):
    th = table.find("th", string=field_name)
    return th.find_next("td").get_text(strip=True) if th else None


def update_car_details(car, color, transmission, engine_capacity, car_fuel):
    if color:
        car.color = color
    if transmission:
        car.transmission = transmission
    if engine_capacity:
        car.engine_capacity = engine_capacity
    if car_fuel:
        car.car_fuel = car_fuel


def process_cars():
    session = Session()
    try:
        cars = session.query(TimeDealCar).all()

        for car in cars:
            car_details_html = fetch_car_details(car.id_car)
            if car_details_html:
                try:
                    color, transmission, engine_capacity, car_fuel = parse_car_details(car_details_html)
                    update_car_details(car, color, transmission, engine_capacity, car_fuel)
                    session.commit()
                except Exception as e:
                    logger.warning(f"Ошибка обработки данных для {car.id_car}: {e}")
                    session.rollback()
    finally:
        session.close()

    logger.info("Процесс обновления данных завершен.")


def main():
    process_cars()


if __name__ == "__main__":
    main()

import requests
import logging
from mpark.site_mpark import Session, TimeDealCar

logging.basicConfig(
    filename="../app.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def fetch_car_details(id_car):
    url = f"https://api.m-park.co.kr/home/api/v1/wb/searchmycar/cardetailinfo/get?demoNo={id_car}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при выполнении запроса к API для {id_car}: {e}")
        return None


def update_car_info(car, details):
    try:
        car_color = details.get("carColor", None)
        engine_capacity = details.get("numCc", None)
        car_type = details.get("carType", None)
        car_name = details.get("carName", None)
        price = details.get("demoAmt", None)
        year = details.get("yymm", None)
        millage = details.get("km", None)
        car_fuel = details.get("carGas", None)
        car_noAccident = details.get("noAccident", None)
        transmission = details.get("carAutoGbn", None)
        images = details.get("images", [])
        image_urls = ",".join(images)
        main_image = images[0] if images else None

        car.car_color = car_color
        car.engine_capacity = engine_capacity
        car.car_type = car_type
        car.car_name = car_name
        car.price = price
        car.year = year
        car.millage = millage
        car.car_fuel = car_fuel
        car.car_noAccident = car_noAccident
        car.transmission = transmission
        car.images = image_urls
        car.main_image = main_image
    except Exception as e:
        logger.warning(f"Ошибка обработки данных для {car.id_car}: {e}")
        raise


def process_cars():
    session = Session()

    try:
        cars = session.query(TimeDealCar).all()
        for car in cars:
            car_details = fetch_car_details(car.id_car)
            if car_details:
                try:
                    details = car_details.get("data", {}).get("detailInfo", [])[0]
                    update_car_info(car, details)
                    session.commit()
                except Exception as e:
                    logger.warning(f"Ошибка обновления данных для {car.id_car}: {e}")
                    session.rollback()
    finally:
        session.close()


def main():
    process_cars()
    logger.info("Процесс обновления данных завершен.")


if __name__ == "__main__":
    main()

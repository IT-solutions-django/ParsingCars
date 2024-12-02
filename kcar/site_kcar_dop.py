import requests
import logging
from kcar.site_kcar import Session, TimeDealCar

logging.basicConfig(
    filename="../app.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def fetch_car_details(id_car):
    url = f"https://api.kcar.com/bc/car-info-detail-of-ng?i_sCarCd={id_car}&i_sPassYn=N&bltbdKnd=CM050"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при выполнении запроса к API для {id_car}: {e}")
        return None


def update_car_details(car, car_details, session):
    try:
        details = car_details.get("data", {}).get("rvo", {})
        car_type = details.get("carctgr", None)
        car_transmission = details.get("trnsmsncdNm", None)
        car_fuel = details.get("fuelTypecdNm", None)
        car_noAccident = details.get("acdtHistComnt", None)
        drive = details.get("drvgYnNm", None)

        images_list = [image["elanPath"] for image in car_details.get("data", {}).get("photoList", [])]
        res_images = ', '.join(images_list)

        car.transmission = car_transmission
        car.car_type = car_type
        car.car_fuel = car_fuel
        car.car_noAccident = car_noAccident
        car.drive = drive
        car.images = res_images

        session.commit()
    except Exception as e:
        logger.warning(f"Ошибка обработки данных для {car.id_car}: {e}")
        session.rollback()


def process_cars():
    session = Session()
    try:
        cars = session.query(TimeDealCar).all()
        for car in cars:
            car_details = fetch_car_details(car.id_car)
            if car_details:
                update_car_details(car, car_details, session)
    except Exception as e:
        logger.error(f"Ошибка обработки автомобилей: {e}")
    finally:
        session.close()


def main():
    process_cars()
    logger.info("Процесс обновления данных завершен.")


if __name__ == "__main__":
    main()

from kcar.site_kcar import TimeDealCar
from utils.log import logger
from utils.db import Session
from utils.request_api import fetch_car_details_json


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
            url = f"https://api.kcar.com/bc/car-info-detail-of-ng?i_sCarCd={car.id_car}&i_sPassYn=N&bltbdKnd=CM050"
            car_details = fetch_car_details_json(url, car.id_car)
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

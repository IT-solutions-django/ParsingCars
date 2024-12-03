from kbchachacha.site_kbchachacha import TimeDealCar
from utils.log import logger
from utils.db import Session
from utils.request_api import fetch_post_car_details_json


def update_car_details(car, car_details, session):
    try:
        details = car_details.get("list", [])[0]
        car_name = details.get("makerName ") + details.get("className ") + details.get("carName ") + details.get(
            "modelName ") + details.get("gradeName")
        year = details.get("yymm")
        millage = details.get("km")
        price = details.get("sellAmt")
        images = details.get("photoName1")
        main_image = images
        color = details.get("colorName")
        car_fuel = details.get("gasName")
        transmission = details.get("autoGbnName")
        car_noAccident = details.get("accidentNo")
        engine_capacity = details.get("numCc")
        url_car = f"https://www.kbchachacha.com/public/car/detail.kbc?carSeq={car.id_car}"

        car.transmission = transmission
        car.car_fuel = car_fuel
        car.car_noAccident = car_noAccident
        car.images = images
        car.main_image = main_image
        car.year = year
        car.car_name = car_name
        car.millage = millage
        car.price = price
        car.color = color
        car.engine_capacity = engine_capacity
        car.url_car = url_car

        session.commit()
    except Exception as e:
        logger.warning(f"Ошибка обработки данных для {car.id_car}: {e}")
        session.rollback()


def process_cars():
    session = Session()
    try:
        cars = session.query(TimeDealCar).all()
        for car in cars:
            url = f"https://www.kbchachacha.com/public/car/common/recent/car/list.json"
            data = {
                "gotoPage": 1,
                "pageSize": 30,
                "carSeqVal": car.id_car
            }
            car_details = fetch_post_car_details_json(url, car.id_car, data)
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

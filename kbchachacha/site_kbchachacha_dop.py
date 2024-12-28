import random
from kbchachacha.site_kbchachacha import TimeDealCar
from utils.log import logger
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from aiohttp import ClientSession
from sqlalchemy import select
from bs4 import BeautifulSoup


async def update_car_details(car_id, async_session, price, year, millage, car_fuel, transmission, car_type, color,
                             images,
                             main_image, engine_capacity):
    async with async_session as session:
        try:
            car = await session.execute(
                select(TimeDealCar).filter_by(id_car=car_id)
            )
            car = car.scalars().first()
            if not car:
                logger.warning(f"Машина с id {car_id} не найдена.")
                return None

            car.transmission = transmission
            car.car_fuel = car_fuel
            car.images = images
            car.year = year
            car.millage = millage
            car.price = price
            car.color = color
            car.main_image = main_image
            car.car_type = car_type
            car.engine_capacity = engine_capacity

            await session.commit()
        except Exception as e:
            logger.warning(f"Ошибка обработки данных для {car.id_car}: {e}")
            await session.rollback()
            return None


def detect_captcha(response):
    logger.error("Капча")
    soup = BeautifulSoup(response, "html.parser")
    scripts = soup.find_all("script")
    for script in scripts:
        if "src" in script.attrs:
            captcha = script["src"]
            if "recaptcha" in captcha:
                return True
    return False


async def request(http_session, url, retries=3):
    cookie_string = (
        "cha-cid=df38aea4-c0e9-415d-a09b-1801b656bc52; "
        "_fwb=145F4gLBeK32zxB7QYyRsyy.1732261933668; "
        "WMONID=GAszeW2Qj7u; "
        "_fcOM={\"k\":\"94126c516594be0c4db0b17819352daff7243c5\",\"i\":\"178.49.227.252\",\"r\":1732261942105}; "
        "_m_uid=3988ccd0-c3d0-3775-9496-408c99876971; "
        "_m_uid_type=A; "
        "_m_uidt=C; "
        "_gid=GA1.2.870553345.1735302205; "
        "TR10062602448_t_uid=12164957018225748.1735302208447; "
        "_clck=190fz6y%7C2%7Cfs2%7C0%7C1787; "
        "wcs_bt=unknown:1735302541; "
        "_ga=GA1.1.1697241224.1732262019; "
        "_clsk=q2tvg6%7C1735302542124%7C2%7C1%7Ce.clarity.ms%2Fcollect; "
        "page-no-action-count=0; "
        "_ga_BQD4DF40J4=GS1.1.1735302234.16.1.1735302699.60.0.1604808303; "
        "JSESSIONID=E9JuacvX9bd8R0eDawIlyM7A1JJKRQAUwuCJolyGnE7evEDov53YGRafiwT2RAgw.cGNoYWFwbzFfZG9tYWluL0NBUjNBUF9zZXJ2ZXIxX2Nz"
    )
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.86 Safari/537.36",
        "Accept-Language": "ru-RU,ru;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "https://www.kbchachacha.com/",
        "Connection": "keep-alive",
        "Cookie": cookie_string
    }

    for attempt in range(1, retries + 1):
        try:
            async with http_session.get(url, headers=headers,
                                        timeout=100) as response:
                response.raise_for_status()
                text = await response.text()
                if detect_captcha(text):
                    await asyncio.sleep(2 ** attempt)
                else:
                    return text
        except Exception as e:
            logger.error(f"Ошибка при выполнении запроса к API: {e}")
            await asyncio.sleep(random.uniform(1, 3))

    return None


def parse_html(response):
    soup = BeautifulSoup(response, "html.parser")
    price_tag = soup.find("div", class_="car-buy-price")
    if price_tag:
        price = price_tag.find("dt", string="판매가격")
        if price:
            price = price.find_next_sibling("dd").get_text(strip=True)
        else:
            price = None
    else:
        price = None

    table = soup.find("table", class_="detail-info-table")
    if not table:
        logger.warning("Не удалось найти таблицу с деталями автомобиля")
        return None

    year = table.find("th", string="연식")
    if year:
        year = year.find_next("td").get_text(strip=True)
    else:
        year = None

    millage = table.find("th", string="주행거리")
    if millage:
        millage = millage.find_next("td").get_text(strip=True)
    else:
        millage = None

    car_fuel = table.find("th", string="연료")
    if car_fuel:
        car_fuel = car_fuel.find_next("td").get_text(strip=True)
    else:
        car_fuel = None

    transmission = table.find("th", string="변속기")
    if transmission:
        transmission = transmission.find_next("td").get_text(strip=True)
    else:
        transmission = None

    car_type = table.find("th", string="차종")
    if car_type:
        car_type = car_type.find_next("td").get_text(strip=True)
    else:
        car_type = None

    color = table.find("th", string="색상")
    if color:
        color = color.find_next("td").get_text(strip=True)
    else:
        color = None

    engine_capacity = table.find("th", string="배기량")
    if engine_capacity:
        engine_capacity = engine_capacity.find_next("td").get_text(strip=True)
    else:
        engine_capacity = None

    images_tag = soup.find("div", class_="page01")
    images = []

    if images_tag:
        for image in images_tag.find_all("a"):
            img_tag = image.find("img")
            if img_tag and "src" in img_tag.attrs:
                images.append(img_tag["src"])

    if images:
        main_image = images[0]
    else:
        main_image = None

    images = ",".join(images)

    return price, year, millage, car_fuel, transmission, car_type, color, images, main_image, engine_capacity


async def process_car(http_session, async_session, car):
    url = f"https://www.kbchachacha.com/public/car/detail.kbc?carSeq={car.id_car}"
    response = await request(http_session, url)

    if response:
        parsed_data = parse_html(response)

        if parsed_data:
            price, year, millage, car_fuel, transmission, car_type, color, images, main_image, engine_capacity = parsed_data
            await update_car_details(car.id_car, async_session, price, year, millage, car_fuel, transmission, car_type,
                                     color,
                                     images, main_image, engine_capacity)
        else:
            logger.warning(f"Не удалось извлечь данные для машины с id {car.id_car}.")
            return None
    else:
        logger.error(f"Ошибка при получении данных для машины с id {car.id_car}.")
        return None

    await asyncio.sleep(random.uniform(2, 5))


async def limited_process_car(http_session, async_session_factory, car, semaphore):
    async with semaphore:
        async with async_session_factory() as session:
            await process_car(http_session, session, car)
            await asyncio.sleep(random.uniform(5, 10))


async def process_cars():
    semaphore = asyncio.Semaphore(5)
    async_engine = create_async_engine("sqlite+aiosqlite:///cars_2.db")
    async_session_factory = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)

    try:
        async with async_session_factory() as session:
            result = await session.execute(select(TimeDealCar))
            cars = result.scalars().all()
    except Exception as e:
        logger.error(f"Ошибка извлечения данных из БД: {e}")
        return

    async with ClientSession() as http_session:
        try:
            tasks = [limited_process_car(http_session, async_session_factory, car, semaphore) for car in cars]
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Ошибка при обработке машин: {e}")
            return


def main():
    asyncio.run(process_cars())
    logger.info("Процесс обновления данных завершен.")


if __name__ == "__main__":
    main()
